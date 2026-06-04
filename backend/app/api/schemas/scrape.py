from pydantic import BaseModel, Field


class ScrapeResponse(BaseModel):
    """
    Result returned by POST /scrape after a full scrape-and-ingest cycle.
    Mirrors IngestionResult but adds scraper-level context.
    """

    inserted: int = Field(ge=0, description="New articles written to the database")
    duplicates: int = Field(ge=0, description="Articles already in the database (skipped)")
    failed: int = Field(ge=0, description="Articles that failed validation or insert")
    total_scraped: int = Field(ge=0, description="Raw articles returned by all scrapers")
    sources_scraped: list[str] = Field(description="Source names that ran successfully")
    duration_seconds: float = Field(ge=0, description="Wall-clock time for the full cycle")
