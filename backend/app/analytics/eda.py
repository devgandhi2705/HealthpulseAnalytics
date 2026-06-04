from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.api.schemas.eda import (
    CategoryOverTimeReport,
    CategorySeries,
    EDAReport,
    KeywordItem,
    KeywordReport,
    MonthlyPoint,
    SourceGrowthReport,
    SourceSeries,
)
from app.models.article import Article

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword extraction config
# ---------------------------------------------------------------------------

# Match only alphabetic words between 3–20 characters.
# This naturally strips numbers, URLs, and junk tokens.
_WORD_RE = re.compile(r"\b[a-zA-Z]{3,20}\b")

_TOP_N_DEFAULT = 30

# Common English function words + overly broad health-news terms that would
# dominate any corpus without adding insight.
_STOPWORDS: frozenset[str] = frozenset({
    # Articles / determiners
    "the", "this", "these", "those", "that", "its", "their", "our",
    # Prepositions
    "for", "with", "from", "into", "about", "upon", "over", "under",
    "between", "through", "during", "after", "before", "within",
    # Conjunctions / connectors
    "and", "but", "nor", "not", "yet", "however", "therefore",
    "because", "while", "although", "including", "according",
    # Auxiliary verbs
    "are", "was", "were", "been", "have", "has", "had", "will",
    "would", "could", "should", "may", "might", "can",
    # Pronouns
    "they", "them", "there", "their", "also", "each", "such",
    # Common filler words
    "said", "says", "say", "use", "used", "more", "most", "than",
    "some", "any", "all", "just", "only", "very", "well", "both",
    "when", "how", "what", "which", "who", "per", "new", "one",
    "two", "three", "first", "last", "year", "years", "then",
})

# ---------------------------------------------------------------------------
# DB columns loaded for EDA — includes text for keyword analysis.
# ---------------------------------------------------------------------------

_EDA_COLS = [
    Article.id,
    Article.source,
    Article.category,
    Article.published_date,
    Article.title,
    Article.article_text,
]


class EDAService:
    """
    Exploratory data analytics over the full article corpus.

    Loads one DataFrame per request (cached on the instance) so
    get_full_report() only hits the database once regardless of how many
    individual methods it calls.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._df: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_full_report(self, top_n: int = _TOP_N_DEFAULT) -> EDAReport:
        """Return all four EDA metrics in a single response."""
        return EDAReport(
            keywords=self.get_keywords(top_n),
            monthly_trend=self.get_monthly_trend(),
            source_growth=self.get_source_growth(),
            category_over_time=self.get_category_over_time(),
        )

    def get_keywords(self, top_n: int = _TOP_N_DEFAULT) -> KeywordReport:
        """
        Extract the most frequent keywords from the article corpus.

        Prefers article_text; falls back to title when text is absent.
        Removes stopwords and tokens outside [3, 20] characters.
        """
        df = self._dataframe()
        if df.empty:
            return KeywordReport(total_articles_analyzed=0, unique_keywords=0, items=[])

        # Prefer article_text; fall back to title for articles without body.
        text_col = df["article_text"].where(df["article_text"].notna(), df["title"])
        corpus = " ".join(text_col.fillna(""))

        all_words = _WORD_RE.findall(corpus.lower())
        filtered = [w for w in all_words if w not in _STOPWORDS]

        if not filtered:
            return KeywordReport(
                total_articles_analyzed=len(df),
                unique_keywords=0,
                items=[],
            )

        counter = Counter(filtered)
        total_occurrences = len(filtered)

        items = [
            KeywordItem(
                word=word,
                count=count,
                frequency=round(count / total_occurrences * 100, 4),
            )
            for word, count in counter.most_common(top_n)
        ]

        return KeywordReport(
            total_articles_analyzed=len(df),
            unique_keywords=len(counter),
            items=items,
        )

    def get_monthly_trend(self) -> list[MonthlyPoint]:
        """Total articles published per calendar month, sorted ascending."""
        dated = self._dated_df()
        if dated.empty:
            return []

        counts = (
            dated.groupby("month")["id"]
            .count()
            .reset_index(name="count")
            .sort_values("month")
        )
        return [
            MonthlyPoint(month=row.month, count=int(row.count))
            for row in counts.itertuples(index=False)
        ]

    def get_source_growth(self) -> SourceGrowthReport:
        """
        Monthly article counts per source on a shared time axis.
        Zero-fills months where a source published nothing.
        """
        dated = self._dated_df()
        if dated.empty:
            return SourceGrowthReport(months=[], series=[])

        pivot = (
            dated.groupby(["month", "source"])["id"]
            .count()
            .unstack(fill_value=0)
        )
        months = sorted(pivot.index.tolist())
        pivot = pivot.reindex(months, fill_value=0)

        series = [
            SourceSeries(
                source=str(source),
                data=[
                    MonthlyPoint(month=m, count=int(pivot.at[m, source]))
                    for m in months
                ],
            )
            for source in pivot.columns
        ]
        return SourceGrowthReport(months=months, series=series)

    def get_category_over_time(self) -> CategoryOverTimeReport:
        """
        Monthly article counts per category on a shared time axis.
        Zero-fills months where a category had no articles.
        """
        dated = self._dated_df()
        if dated.empty:
            return CategoryOverTimeReport(months=[], series=[])

        pivot = (
            dated.groupby(["month", "category"])["id"]
            .count()
            .unstack(fill_value=0)
        )
        months = sorted(pivot.index.tolist())
        pivot = pivot.reindex(months, fill_value=0)

        series = [
            CategorySeries(
                category=str(cat),
                data=[
                    MonthlyPoint(month=m, count=int(pivot.at[m, cat]))
                    for m in months
                ],
            )
            for cat in pivot.columns
        ]
        return CategoryOverTimeReport(months=months, series=series)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _dataframe(self) -> pd.DataFrame:
        """Load and cache the full EDA DataFrame for this request."""
        if self._df is not None:
            return self._df

        rows = self.db.query(*_EDA_COLS).all()

        self._df = pd.DataFrame(
            rows or [],
            columns=["id", "source", "category", "published_date", "title", "article_text"],
        )
        logger.debug("EDA DataFrame loaded: %d rows", len(self._df))
        return self._df

    def _dated_df(self) -> pd.DataFrame:
        """
        Subset of the DataFrame restricted to rows with a valid published_date,
        with a pre-computed 'month' column (ISO year-month string).
        Only articles with a known date are included in time-series analytics.
        """
        df = self._dataframe()
        if df.empty:
            return df

        dated = df.dropna(subset=["published_date"]).copy()
        if dated.empty:
            return dated

        dated["month"] = (
            pd.to_datetime(dated["published_date"])
            .dt.to_period("M")
            .astype(str)
        )
        return dated
