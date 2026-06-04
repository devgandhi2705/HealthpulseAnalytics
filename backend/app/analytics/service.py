from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.api.schemas.analytics import (
    AnalyticsSummary,
    CategoryCount,
    DailyCount,
    MostActiveSource,
    SourceCount,
)
from app.models.article import Article

logger = logging.getLogger(__name__)

# Columns fetched from the DB — keeps the DataFrame lean.
_ANALYTICS_COLUMNS = [
    Article.id,
    Article.source,
    Article.category,
    Article.published_date,
]


class AnalyticsService:
    """
    All analytics are computed from a single in-memory DataFrame built per
    request.  Each public method is independently callable; get_summary()
    composes them into one response object for the dashboard endpoint.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._df: Optional[pd.DataFrame] = None  # lazy-loaded once per instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_summary(self) -> AnalyticsSummary:
        """Return all five analytics metrics in a single response."""
        return AnalyticsSummary(
            total_articles=self.total_articles(),
            articles_per_source=self.articles_per_source(),
            articles_per_category=self.articles_per_category(),
            daily_trend=self.daily_trend(),
            most_active_source=self.most_active_source(),
        )

    def total_articles(self) -> int:
        """Total number of articles currently stored."""
        return len(self._dataframe())

    def articles_per_source(self) -> list[SourceCount]:
        """Article count for each source, sorted descending by count."""
        df = self._dataframe()
        if df.empty:
            return []

        counts = (
            df.groupby("source", sort=False)["id"]
            .count()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        return [
            SourceCount(source=row.source, count=int(row.count))
            for row in counts.itertuples(index=False)
        ]

    def articles_per_category(self) -> list[CategoryCount]:
        """Article count for each category, sorted descending by count."""
        df = self._dataframe()
        if df.empty:
            return []

        counts = (
            df.groupby("category", sort=False)["id"]
            .count()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        return [
            CategoryCount(category=row.category, count=int(row.count))
            for row in counts.itertuples(index=False)
        ]

    def daily_trend(self) -> list[DailyCount]:
        """
        Article count per calendar day based on published_date.
        Articles without a published_date are excluded.
        Results are sorted ascending (oldest → newest).
        """
        df = self._dataframe()
        if df.empty:
            return []

        dated = df.dropna(subset=["published_date"]).copy()
        if dated.empty:
            return []

        dated["day"] = pd.to_datetime(dated["published_date"]).dt.normalize()
        counts = (
            dated.groupby("day")["id"]
            .count()
            .reset_index(name="count")
            .sort_values("day")
        )
        return [
            DailyCount(date=row.day.date(), count=int(row.count))
            for row in counts.itertuples(index=False)
        ]

    def most_active_source(self) -> Optional[MostActiveSource]:
        """
        Source with the highest article count.
        Returns None when the database is empty.
        """
        df = self._dataframe()
        if df.empty:
            return None

        counts = df.groupby("source")["id"].count()
        top_source = counts.idxmax()
        return MostActiveSource(source=top_source, count=int(counts[top_source]))

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _dataframe(self) -> pd.DataFrame:
        """
        Load analytics columns from the DB into a DataFrame.
        The result is cached for the lifetime of this service instance
        so multiple analytic calls in get_summary() hit the DB only once.
        """
        if self._df is not None:
            return self._df

        rows = self.db.query(*_ANALYTICS_COLUMNS).all()

        if not rows:
            self._df = pd.DataFrame(
                columns=["id", "source", "category", "published_date"]
            )
        else:
            self._df = pd.DataFrame(
                rows,
                columns=["id", "source", "category", "published_date"],
            )

        logger.debug("Analytics DataFrame loaded: %d rows", len(self._df))
        return self._df
