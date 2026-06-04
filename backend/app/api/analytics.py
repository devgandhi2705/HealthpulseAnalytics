from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.service import AnalyticsService
from app.api.schemas.analytics import (
    CategoryDistributionResponse,
    CategoryShare,
    DailyTrendResponse,
    OverviewResponse,
    SourceDistributionResponse,
    SourceShare,
    TrendPoint,
)
from app.database.session import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

def _service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Inject a per-request AnalyticsService with a cached DataFrame."""
    return AnalyticsService(db)


# ---------------------------------------------------------------------------
# GET /analytics/overview
# ---------------------------------------------------------------------------

@router.get(
    "/overview",
    response_model=OverviewResponse,
    summary="Dashboard overview",
    description="""
Returns high-level statistics for the main dashboard summary cards:

- **total_articles** — total records stored
- **sources_count** — number of distinct news sources
- **categories_count** — number of distinct categories
- **most_active_source** — source with the most articles (`null` when empty)

All four values are derived from a single database query.
""",
)
def get_overview(svc: AnalyticsService = Depends(_service)) -> OverviewResponse:
    sources = svc.articles_per_source()
    categories = svc.articles_per_category()

    return OverviewResponse(
        total_articles=svc.total_articles(),
        sources_count=len(sources),
        categories_count=len(categories),
        most_active_source=svc.most_active_source(),
    )


# ---------------------------------------------------------------------------
# GET /analytics/source-distribution
# ---------------------------------------------------------------------------

@router.get(
    "/source-distribution",
    response_model=SourceDistributionResponse,
    summary="Article distribution by source",
    description="""
Returns article counts and percentage share for each news source.

Items are **sorted descending by count** so the dominant source is always first —
ready to feed directly into a pie or horizontal bar chart.

`percentage` values sum to 100 (within floating-point rounding).
""",
)
def get_source_distribution(
    svc: AnalyticsService = Depends(_service),
) -> SourceDistributionResponse:
    sources = svc.articles_per_source()
    total = sum(s.count for s in sources)

    items = [
        SourceShare(
            source=s.source,
            count=s.count,
            percentage=round(s.count / total * 100, 2) if total else 0.0,
        )
        for s in sources
    ]

    return SourceDistributionResponse(total=total, items=items)


# ---------------------------------------------------------------------------
# GET /analytics/category-distribution
# ---------------------------------------------------------------------------

@router.get(
    "/category-distribution",
    response_model=CategoryDistributionResponse,
    summary="Article distribution by category",
    description="""
Returns article counts and percentage share for each category.

Items are **sorted descending by count**.
`percentage` values sum to 100 (within floating-point rounding).
""",
)
def get_category_distribution(
    svc: AnalyticsService = Depends(_service),
) -> CategoryDistributionResponse:
    categories = svc.articles_per_category()
    total = sum(c.count for c in categories)

    items = [
        CategoryShare(
            category=c.category,
            count=c.count,
            percentage=round(c.count / total * 100, 2) if total else 0.0,
        )
        for c in categories
    ]

    return CategoryDistributionResponse(total=total, items=items)


# ---------------------------------------------------------------------------
# GET /analytics/daily-trend
# ---------------------------------------------------------------------------

@router.get(
    "/daily-trend",
    response_model=DailyTrendResponse,
    summary="Daily publishing trend",
    description="""
Returns a time-series of published article counts per calendar day.

- Points are sorted **ascending** (oldest → newest) for direct use in
  line or area charts.
- **data_points** tells the frontend how many entries to expect without
  inspecting the array.
- Articles without a `published_date` are excluded from this series.
""",
)
def get_daily_trend(svc: AnalyticsService = Depends(_service)) -> DailyTrendResponse:
    trend = svc.daily_trend()

    items = [TrendPoint(date=point.date, count=point.count) for point in trend]

    return DailyTrendResponse(data_points=len(items), items=items)
