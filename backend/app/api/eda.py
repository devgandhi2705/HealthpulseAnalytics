from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.analytics.eda import EDAService
from app.api.schemas.eda import (
    CategoryOverTimeReport,
    EDAReport,
    KeywordReport,
    MonthlyPoint,
    SourceGrowthReport,
)
from app.database.session import get_db

router = APIRouter(prefix="/eda", tags=["eda"])

TopNParam = Annotated[
    int,
    Query(ge=1, le=200, description="Maximum number of keywords to return"),
]


def _svc(db: Session = Depends(get_db)) -> EDAService:
    return EDAService(db)


# ---------------------------------------------------------------------------
# GET /eda/report
# ---------------------------------------------------------------------------

@router.get(
    "/report",
    response_model=EDAReport,
    summary="Full EDA report",
    description="""
Returns all four EDA datasets in a single request — optimised for dashboard
initial load.  All four analyses share one database query.

- **keywords** — top words by frequency across article text and titles
- **monthly_trend** — total articles published per calendar month
- **source_growth** — per-source monthly counts on a shared time axis
- **category_over_time** — per-category monthly counts on a shared time axis
""",
)
def get_report(
    top_n: TopNParam = 30,
    svc: EDAService = Depends(_svc),
) -> EDAReport:
    return svc.get_full_report(top_n=top_n)


# ---------------------------------------------------------------------------
# Individual endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/keywords",
    response_model=KeywordReport,
    summary="Top keywords by frequency",
    description="""
Tokenises article body text (falls back to title when body is absent),
removes common stopwords, and returns the most frequent terms.

Use `top_n` to control how many keywords are returned (default 30, max 200).
""",
)
def get_keywords(
    top_n: TopNParam = 30,
    svc: EDAService = Depends(_svc),
) -> KeywordReport:
    return svc.get_keywords(top_n=top_n)


@router.get(
    "/monthly-trend",
    response_model=list[MonthlyPoint],
    summary="Total articles published per month",
    description="""
Articles grouped by the calendar month of their `published_date`.
Only articles with a known publication date are included.
Points are sorted ascending (oldest → newest).
""",
)
def get_monthly_trend(svc: EDAService = Depends(_svc)) -> list[MonthlyPoint]:
    return svc.get_monthly_trend()


@router.get(
    "/source-growth",
    response_model=SourceGrowthReport,
    summary="Monthly article counts per source",
    description="""
Returns a shared month axis and one data series per news source.
Months where a source published nothing are filled with zero so every
series has the same length — ready to drop into a grouped bar or
multi-line chart without client-side alignment.
""",
)
def get_source_growth(svc: EDAService = Depends(_svc)) -> SourceGrowthReport:
    return svc.get_source_growth()


@router.get(
    "/category-over-time",
    response_model=CategoryOverTimeReport,
    summary="Monthly article counts per category",
    description="""
Returns a shared month axis and one data series per category.
Zero-filled months ensure all series are the same length.
Suitable for stacked bar or grouped line charts.
""",
)
def get_category_over_time(svc: EDAService = Depends(_svc)) -> CategoryOverTimeReport:
    return svc.get_category_over_time()
