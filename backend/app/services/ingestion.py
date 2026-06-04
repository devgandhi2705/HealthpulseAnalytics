from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.article import Article
from app.scraper.base import ScrapedArticle

logger = logging.getLogger(__name__)

SUMMARY_MAX_CHARS = 300


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IngestionResult:
    """Counters returned after a single ingestion run."""

    inserted: int
    duplicates: int
    failed: int

    @property
    def total(self) -> int:
        return self.inserted + self.duplicates + self.failed


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class IngestionService:
    """
    Validates, deduplicates, normalises, and persists scraped articles.

    Each call to ingest() issues one database transaction.  Individual
    article failures are isolated with savepoints so a bad row cannot
    roll back an otherwise clean batch.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest(self, articles: list[ScrapedArticle]) -> IngestionResult:
        """
        Process *articles* and persist the valid, unique ones to the DB.
        Returns an IngestionResult with counts of what happened.
        """
        inserted = duplicates = failed = 0
        scraped_at = datetime.now(timezone.utc)

        # Step 1 — remove duplicates within the incoming batch.
        unique, batch_dups = self._deduplicate_batch(articles)
        duplicates += batch_dups

        # Step 2 — remove URLs already present in the DB (single bulk query).
        existing_urls = self._fetch_existing_urls({a.url for a in unique})
        candidates: list[ScrapedArticle] = []
        for article in unique:
            if article.url in existing_urls:
                logger.debug("DB duplicate skipped: %s", article.url)
                duplicates += 1
            else:
                candidates.append(article)

        # Step 3 — validate and insert each candidate.
        for article in candidates:
            if not self._validate(article):
                failed += 1
                continue

            try:
                # Savepoint per row: one bad insert cannot poison the batch.
                with self.db.begin_nested():
                    self.db.add(self._to_model(article, scraped_at))
                inserted += 1
            except SQLAlchemyError as exc:
                logger.warning("Insert failed for %r: %s", article.url, exc)
                failed += 1

        # Step 4 — flush all savepoints to the DB in one commit.
        try:
            self.db.commit()
        except SQLAlchemyError as exc:
            logger.error("Batch commit failed — rolling back: %s", exc)
            self.db.rollback()
            failed += inserted
            inserted = 0

        result = IngestionResult(inserted=inserted, duplicates=duplicates, failed=failed)
        self._log_result(result)
        return result

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_batch(
        articles: list[ScrapedArticle],
    ) -> tuple[list[ScrapedArticle], int]:
        """
        Strip duplicate URLs from the incoming list.
        Returns (unique_articles, duplicate_count).
        First occurrence of a URL wins.
        """
        seen: set[str] = set()
        unique: list[ScrapedArticle] = []
        dups = 0
        for article in articles:
            if article.url in seen:
                dups += 1
            else:
                seen.add(article.url)
                unique.append(article)
        return unique, dups

    def _fetch_existing_urls(self, urls: set[str]) -> set[str]:
        """Return the subset of *urls* already stored in the DB."""
        if not urls:
            return set()
        rows = self.db.query(Article.url).filter(Article.url.in_(urls)).all()
        return {row.url for row in rows}

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate(article: ScrapedArticle) -> bool:
        """
        Return True when the article has all fields required for a clean DB row.
        Logs a warning for each rejected article.
        """
        problems: list[str] = []

        if not (article.title or "").strip():
            problems.append("missing title")
        if not (article.url or "").strip():
            problems.append("missing url")
        if not (article.source or "").strip():
            problems.append("missing source")
        if not (article.category or "").strip():
            problems.append("missing category")

        if problems:
            logger.warning(
                "Dropping article (url=%r): %s",
                article.url,
                ", ".join(problems),
            )
            return False

        return True

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_date(dt: Optional[datetime]) -> Optional[datetime]:
        """
        Ensure a datetime is timezone-aware.
        Naive datetimes are assumed to be UTC.
        """
        if dt is None:
            return None
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

    @staticmethod
    def _make_summary(article: ScrapedArticle) -> Optional[str]:
        """
        Return the first SUMMARY_MAX_CHARS characters of the article summary.
        Appends an ellipsis when the text is truncated.
        Returns None when no summary text is available.

        Replace this method with an LLM call once AI summarisation is ready.
        """
        text = (article.summary or "").strip()
        if not text:
            return None
        if len(text) <= SUMMARY_MAX_CHARS:
            return text
        return text[:SUMMARY_MAX_CHARS].rstrip() + "…"  # …

    # ------------------------------------------------------------------
    # Mapping
    # ------------------------------------------------------------------

    def _to_model(self, article: ScrapedArticle, scraped_at: datetime) -> Article:
        """Convert a ScrapedArticle into an ORM Article ready for insertion."""
        return Article(
            title=article.title.strip(),
            source=article.source.strip(),
            category=article.category.strip(),
            summary=self._make_summary(article),
            url=article.url.strip(),
            published_date=self._normalize_date(article.published_date),
            scraped_date=scraped_at,
            article_text=article.article_text or None,
        )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    @staticmethod
    def _log_result(result: IngestionResult) -> None:
        logger.info(
            "Ingestion complete — inserted: %d | duplicates: %d | failed: %d | total: %d",
            result.inserted,
            result.duplicates,
            result.failed,
            result.total,
        )
