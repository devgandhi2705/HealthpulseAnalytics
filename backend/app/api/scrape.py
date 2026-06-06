import logging
import threading
import time

from fastapi import APIRouter, HTTPException, status

from app.database.session import SessionLocal
from app.scraper import get_all_scrapers
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["scraper"])

# Prevent concurrent scrape runs.
_lock = threading.Lock()

# Shared state updated by the background scrape thread.
# Readers only need eventual consistency, so a plain dict is fine here.
_state: dict = {
    "phase": "idle",   # idle | initializing | collecting | processing | saving | complete | error
    "message": "",
    "result": None,    # dict with counts when phase == complete
    "error": None,     # str when phase == error
}


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/scrape/status",
    summary="Return the current scrape phase and progress message",
)
def get_scrape_status() -> dict:
    return _state


@router.post(
    "/scrape",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a full scrape-and-ingest cycle (runs in background)",
    description="""
Starts the scrape pipeline in a background thread and returns immediately.
Poll **GET /scrape/status** to track progress through phases:
`initializing → collecting → processing → saving → complete`.

Returns **409** if a scrape is already in progress.
""",
)
def run_scrape() -> dict:
    if not _lock.acquire(blocking=False):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A scrape is already in progress. Try again shortly.",
        )

    _state.update({
        "phase": "initializing",
        "message": "Setting up data collection…",
        "result": None,
        "error": None,
    })

    thread = threading.Thread(target=_background_scrape, daemon=True)
    thread.start()

    return {"status": "started"}


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

def _background_scrape() -> None:
    db = SessionLocal()
    started_at = time.monotonic()
    try:
        scrapers = get_all_scrapers()
        logger.info("Scrape started — %d source(s)", len(scrapers))

        _state.update({
            "phase": "collecting",
            "message": f"Querying Google News RSS for {len(scrapers)} healthcare keywords…",
        })

        all_articles = []
        sources_scraped: list[str] = []

        for scraper in scrapers:
            logger.info("Running scraper: %s", scraper.SOURCE_NAME)
            try:
                articles = scraper.scrape()
                all_articles.extend(articles)
                sources_scraped.append(scraper.SOURCE_NAME)
                logger.info("  %s → %d article(s)", scraper.SOURCE_NAME, len(articles))
            except Exception as exc:
                logger.error("Scraper %s failed: %s", scraper.SOURCE_NAME, exc)

        logger.info("Collected %d article(s) total", len(all_articles))

        _state.update({
            "phase": "processing",
            "message": f"Processing {len(all_articles)} articles…",
        })
        time.sleep(0.4)  # give the UI one visible tick at this phase

        _state.update({
            "phase": "saving",
            "message": "Saving to database…",
        })

        result = IngestionService(db).ingest(all_articles)

        elapsed = round(time.monotonic() - started_at, 2)
        _state.update({
            "phase": "complete",
            "message": f"Done! {result.inserted} new article(s) added.",
            "result": {
                "inserted": result.inserted,
                "duplicates": result.duplicates,
                "failed": result.failed,
                "total_scraped": len(all_articles),
                "sources_scraped": sources_scraped,
                "duration_seconds": elapsed,
            },
        })
        logger.info(
            "Scrape complete in %.2fs — inserted=%d duplicates=%d failed=%d",
            elapsed, result.inserted, result.duplicates, result.failed,
        )

    except Exception as exc:
        logger.error("Background scrape failed: %s", exc)
        _state.update({
            "phase": "error",
            "message": "Data collection failed. Please try again.",
            "error": str(exc),
        })
    finally:
        db.close()
        _lock.release()
