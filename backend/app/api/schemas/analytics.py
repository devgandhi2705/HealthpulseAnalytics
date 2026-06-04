from __future__ import annotations

from datetime import date as _Date
from typing import Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Internal service types (used by AnalyticsService — do not rename)
# ---------------------------------------------------------------------------

class SourceCount(BaseModel):
    source: str
    count: int = Field(ge=0)


class CategoryCount(BaseModel):
    category: str
    count: int = Field(ge=0)


class DailyCount(BaseModel):
    date: _Date
    count: int = Field(ge=0)


class MostActiveSource(BaseModel):
    source: str
    count: int = Field(ge=0)


class AnalyticsSummary(BaseModel):
    total_articles: int = Field(ge=0)
    articles_per_source: list[SourceCount]
    articles_per_category: list[CategoryCount]
    daily_trend: list[DailyCount]
    most_active_source: Optional[MostActiveSource] = None


# ---------------------------------------------------------------------------
# Frontend-ready API response schemas
# ---------------------------------------------------------------------------

class OverviewResponse(BaseModel):
    """
    High-level stats for dashboard summary cards.
    Combines total count, unique-source/category counts, and top source.
    """

    total_articles: int = Field(
        ge=0,
        description="Total number of articles stored in the database",
        examples=[1240],
    )
    sources_count: int = Field(
        ge=0,
        description="Number of distinct news sources",
        examples=[6],
    )
    categories_count: int = Field(
        ge=0,
        description="Number of distinct article categories",
        examples=[4],
    )
    most_active_source: Optional[MostActiveSource] = Field(
        default=None,
        description="Source with the highest article count; null when database is empty",
    )


class SourceShare(BaseModel):
    """Single row in a source-distribution chart."""

    source: str = Field(description="Source name", examples=["WHO"])
    count: int = Field(ge=0, description="Number of articles from this source")
    percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Share of total articles, rounded to two decimal places",
        examples=[48.75],
    )


class SourceDistributionResponse(BaseModel):
    """
    Full source breakdown — ready for pie or bar charts.
    Items are sorted descending by count.
    """

    total: int = Field(ge=0, description="Sum of all article counts")
    items: list[SourceShare]


class CategoryShare(BaseModel):
    """Single row in a category-distribution chart."""

    category: str = Field(description="Category name", examples=["policy"])
    count: int = Field(ge=0, description="Number of articles in this category")
    percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Share of total articles, rounded to two decimal places",
        examples=[32.10],
    )


class CategoryDistributionResponse(BaseModel):
    """
    Full category breakdown — ready for pie or bar charts.
    Items are sorted descending by count.
    """

    total: int = Field(ge=0, description="Sum of all article counts")
    items: list[CategoryShare]


class TrendPoint(BaseModel):
    """One data point in the daily publishing trend series."""

    date: _Date = Field(description="Calendar day (ISO 8601)", examples=["2025-05-14"])
    count: int = Field(ge=0, description="Number of articles published on this day")


class DailyTrendResponse(BaseModel):
    """
    Time-series data for a line or bar chart.
    Points are sorted ascending (oldest → newest).
    Only articles with a known published_date are included.
    """

    data_points: int = Field(ge=0, description="Number of distinct days in the series")
    items: list[TrendPoint]
