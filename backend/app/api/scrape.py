import logging
import threading
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.scrape import ScrapeResponse
from app.database.session import get_db
from app.scraper import get_all_scrapers
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["scraper"])

# Prevent concurrent scrape runs — a single in-memory lock is sufficient
# because there is no requirement for distributed coordination.
_lock = threading.Lock()


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger a full scrape-and-ingest cycle",
    description="""
Runs every registered scraper sequentially, feeds the collected articles into
the ingestion pipeline, and returns a summary of what happened.

Returns **409** if a scrape is already in progress.

Use this endpoint to populate the database on demand.  Attach it to a cron
job or a task scheduler when you need automated runs without Celery/Redis.
""",
)
def run_scrape(db: Session = Depends(get_db)) -> ScrapeResponse:
    if not _lock.acquire(blocking=False):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A scrape is already in progress. Try again shortly.",
        )

    started_at = time.monotonic()
    try:
        return _execute_scrape(db)
    finally:
        _lock.release()
        elapsed = round(time.monotonic() - started_at, 2)
        logger.info("Scrape cycle finished in %.2fs", elapsed)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _execute_scrape(db: Session) -> ScrapeResponse:
    """
    Run all scrapers, ingest results, and return a structured summary.
    Separated from the route handler so error handling and timing stay clean.
    """
    started_at = time.monotonic()
    scrapers = get_all_scrapers()
    logger.info("Starting scrape cycle — %d source(s) registered", len(scrapers))

    all_articles = []
    sources_scraped: list[str] = []

    for scraper in scrapers:
        logger.info("Running scraper: %s", scraper.SOURCE_NAME)
        try:
            articles = scraper.scrape()
            all_articles.extend(articles)
            sources_scraped.append(scraper.SOURCE_NAME)
            logger.info(
                "  %s → %d article(s) fetched",
                scraper.SOURCE_NAME,
                len(articles),
            )
        except Exception as exc:
            # One failed scraper must not abort the rest.
            logger.error("Scraper %s raised an exception: %s", scraper.SOURCE_NAME, exc)

    logger.info("Total articles collected: %d", len(all_articles))

    result = IngestionService(db).ingest(all_articles)

    return ScrapeResponse(
        inserted=result.inserted,
        duplicates=result.duplicates,
        failed=result.failed,
        total_scraped=len(all_articles),
        sources_scraped=sources_scraped,
        duration_seconds=round(time.monotonic() - started_at, 2),
    )
