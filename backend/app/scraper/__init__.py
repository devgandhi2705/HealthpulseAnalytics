"""
Scraper registry.

To add a new source:
  1. Create app/scraper/sources/<name>.py with a class that extends BaseScraper.
  2. Import it below and add one entry to SCRAPER_REGISTRY.

Nothing else needs to change.
"""

from app.scraper.base import BaseScraper, ScrapedArticle
from app.scraper.sources.cdc import CDCScraper
from app.scraper.sources.healthit import HealthITScraper
from app.scraper.sources.nih import NIHScraper
from app.scraper.sources.who import WHOScraper

# Maps source name → scraper class.
# To add a new source: create sources/<name>.py and add one line here.
SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    WHOScraper.SOURCE_NAME:      WHOScraper,
    CDCScraper.SOURCE_NAME:      CDCScraper,
    NIHScraper.SOURCE_NAME:      NIHScraper,
    HealthITScraper.SOURCE_NAME: HealthITScraper,
}


def get_all_scrapers() -> list[BaseScraper]:
    """Return one initialised instance of every registered scraper."""
    return [cls() for cls in SCRAPER_REGISTRY.values()]


def get_scraper(source_name: str) -> BaseScraper:
    """Return an initialised scraper for *source_name*, or raise KeyError."""
    cls = SCRAPER_REGISTRY[source_name]
    return cls()


__all__ = [
    "BaseScraper",
    "ScrapedArticle",
    "SCRAPER_REGISTRY",
    "get_all_scrapers",
    "get_scraper",
]
