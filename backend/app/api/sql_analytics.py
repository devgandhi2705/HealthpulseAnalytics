from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.sql_analytics import (
    BenchmarkReport,
    CategoryCount,
    MonthlyCount,
    SourceCount,
    SQLSummary,
)
from app.database.session import get_db
from app.services.sql_analytics import SQLAnalyticsService

router = APIRouter(prefix="/sql-analytics", tags=["sql-analytics"])


def _svc(db: Session = Depends(get_db)) -> SQLAnalyticsService:
    return SQLAnalyticsService(db)


# ---------------------------------------------------------------------------
# GET /sql-analytics/summary
# ---------------------------------------------------------------------------

@router.get(
    "/summary",
    response_model=SQLSummary,
    summary="All four SQL analytics in one response",
    description="""
Runs four aggregation queries and returns the results together.

Every query uses `GROUP BY` at the database level — no raw rows are
transferred to Python.  Compare the equivalent pandas endpoint at
`GET /analytics/summary` to observe the architectural difference.
""",
)
def get_summary(svc: SQLAnalyticsService = Depends(_svc)) -> SQLSummary:
    return svc.get_summary()


# ---------------------------------------------------------------------------
# Individual metric endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/total",
    summary="Total article count via SQL COUNT",
)
def get_total(svc: SQLAnalyticsService = Depends(_svc)) -> dict[str, int]:
    """Single `SELECT COUNT(*) FROM articles` — the simplest aggregation."""
    return {"total_articles": svc.total_articles()}


@router.get(
    "/sources",
    response_model=list[SourceCount],
    summary="Articles per source (SQL GROUP BY)",
    description="""
`SELECT source, COUNT(id) FROM articles GROUP BY source ORDER BY count DESC`

Sorted descending so the dominant source is always first.
""",
)
def get_sources(svc: SQLAnalyticsService = Depends(_svc)) -> list[SourceCount]:
    return svc.articles_per_source()


@router.get(
    "/categories",
    response_model=list[CategoryCount],
    summary="Articles per category (SQL GROUP BY)",
    description="""
`SELECT category, COUNT(id) FROM articles GROUP BY category ORDER BY count DESC`
""",
)
def get_categories(svc: SQLAnalyticsService = Depends(_svc)) -> list[CategoryCount]:
    return svc.articles_per_category()


@router.get(
    "/monthly",
    response_model=list[MonthlyCount],
    summary="Articles by month (SQL EXTRACT + GROUP BY)",
    description="""
Groups articles by `(YEAR, MONTH)` of `published_date` using SQLAlchemy's
`extract()`, which maps to `STRFTIME` on SQLite and native `EXTRACT` on
PostgreSQL — no client-side date handling required.

Only articles with a known `published_date` are included.
""",
)
def get_monthly(svc: SQLAnalyticsService = Depends(_svc)) -> list[MonthlyCount]:
    return svc.articles_by_month()


# ---------------------------------------------------------------------------
# GET /sql-analytics/benchmark
# ---------------------------------------------------------------------------

@router.get(
    "/benchmark",
    response_model=BenchmarkReport,
    summary="SQL vs pandas performance comparison",
    description="""
Runs both the SQL and pandas analytics implementations against the live
database and returns side-by-side timing data.

**SQL strategy** — 4 `GROUP BY` queries; only aggregated rows cross the wire.

**Pandas strategy** — 1 raw `SELECT` of metadata columns; aggregation runs
in Python using vectorised pandas operations.

Timings use `time.perf_counter()` (nanosecond resolution).
The `analysis` field explains the results in plain English.
""",
)
def get_benchmark(svc: SQLAnalyticsService = Depends(_svc)) -> BenchmarkReport:
    return svc.benchmark_vs_pandas()
