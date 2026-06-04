from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Keyword analysis
# ---------------------------------------------------------------------------

class KeywordItem(BaseModel):
    word: str = Field(description="Keyword extracted from article text")
    count: int = Field(ge=0, description="Total occurrences across the corpus")
    frequency: float = Field(
        ge=0.0,
        description="Share of total word occurrences (%), rounded to 4 dp",
        examples=[1.4523],
    )


class KeywordReport(BaseModel):
    """Top keywords ranked by occurrence count."""

    total_articles_analyzed: int = Field(ge=0)
    unique_keywords: int = Field(ge=0, description="Distinct keywords after stopword removal")
    items: list[KeywordItem] = Field(description="Keywords sorted descending by count")


# ---------------------------------------------------------------------------
# Time series primitives
# ---------------------------------------------------------------------------

class MonthlyPoint(BaseModel):
    """One data point in any monthly time series."""

    month: str = Field(description="ISO year-month string, e.g. '2025-03'", examples=["2025-03"])
    count: int = Field(ge=0)


# ---------------------------------------------------------------------------
# Source growth
# ---------------------------------------------------------------------------

class SourceSeries(BaseModel):
    """Monthly article counts for a single source."""

    source: str
    data: list[MonthlyPoint] = Field(description="Points sorted ascending by month")


class SourceGrowthReport(BaseModel):
    """
    Multi-series data for a grouped bar or multi-line chart.

    `months` is the shared X-axis; every SourceSeries.data list has the
    same length and the same month ordering.
    """

    months: list[str] = Field(description="Shared X-axis labels, ascending")
    series: list[SourceSeries]


# ---------------------------------------------------------------------------
# Category distribution over time
# ---------------------------------------------------------------------------

class CategorySeries(BaseModel):
    """Monthly article counts for a single category."""

    category: str
    data: list[MonthlyPoint] = Field(description="Points sorted ascending by month")


class CategoryOverTimeReport(BaseModel):
    """
    Multi-series data for a stacked bar or grouped line chart.
    Same structure as SourceGrowthReport — shared month axis + per-series counts.
    """

    months: list[str] = Field(description="Shared X-axis labels, ascending")
    series: list[CategorySeries]


# ---------------------------------------------------------------------------
# Combined report
# ---------------------------------------------------------------------------

class EDAReport(BaseModel):
    """All EDA metrics bundled for a single dashboard fetch."""

    keywords: KeywordReport
    monthly_trend: list[MonthlyPoint] = Field(
        description="Total articles published per month, ascending"
    )
    source_growth: SourceGrowthReport
    category_over_time: CategoryOverTimeReport
