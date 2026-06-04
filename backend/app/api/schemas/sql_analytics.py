from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Query result types
# ---------------------------------------------------------------------------

class SourceCount(BaseModel):
    source: str
    count: int = Field(ge=0)


class CategoryCount(BaseModel):
    category: str
    count: int = Field(ge=0)


class MonthlyCount(BaseModel):
    month: str = Field(description="ISO year-month, e.g. '2025-03'", examples=["2025-03"])
    count: int = Field(ge=0)


class SQLSummary(BaseModel):
    """All four SQL analytics in a single response."""

    total_articles: int = Field(ge=0)
    articles_per_source: list[SourceCount]
    articles_per_category: list[CategoryCount]
    articles_by_month: list[MonthlyCount]


# ---------------------------------------------------------------------------
# Benchmark / comparison types
# ---------------------------------------------------------------------------

class MetricBenchmark(BaseModel):
    """Side-by-side timing for one analytic metric."""

    metric: str = Field(description="Analytic name, e.g. 'per_source'")
    sql_ms: float = Field(ge=0, description="SQL implementation duration (ms)")
    pandas_ms: float = Field(ge=0, description="Pandas implementation duration (ms)")
    winner: str = Field(description="'sql', 'pandas', or 'equivalent'")
    speedup_factor: float = Field(
        ge=0,
        description="How many times faster the winner is (1.0 = equal)",
    )


class BenchmarkReport(BaseModel):
    """
    Full performance comparison between the SQL and pandas analytics
    implementations, measured on the live database.

    Methodology
    -----------
    SQL   — 4 separate GROUP BY queries; only aggregated rows cross the wire.
    Pandas — 1 SELECT of raw columns; aggregation runs in Python via pandas.

    All timings use time.perf_counter() and are in milliseconds.
    """

    total_articles: int = Field(ge=0, description="Row count at the time of benchmarking")

    sql_total_ms: float = Field(ge=0, description="Sum of all four SQL queries")
    sql_breakdown: dict[str, float] = Field(
        description="Per-query durations: total, per_source, per_category, by_month"
    )

    pandas_total_ms: float = Field(ge=0, description="DB load + all four pandas operations")
    pandas_load_ms: float = Field(
        ge=0,
        description="Time for the raw SELECT that populates the DataFrame",
    )
    pandas_compute_ms: float = Field(
        ge=0,
        description="Time for the four in-Python pandas aggregations",
    )

    metrics: list[MetricBenchmark]
    overall_winner: str = Field(description="'sql', 'pandas', or 'equivalent'")
    analysis: str = Field(description="Plain-text explanation of the results")
