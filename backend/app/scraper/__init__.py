"""
Scraper registry — keyword-driven Google News RSS pipeline.

Architecture
------------
Each healthcare keyword maps to one GoogleNewsRSSScraper instance.
The scraper fetches the Google News RSS feed for that keyword and
returns ScrapedArticle objects where:

  source   = publisher name  (e.g. "Reuters", "The Guardian")
  category = search keyword  (e.g. "healthcare", "telemedicine")

This mapping preserves full backward-compatibility with all existing
analytics endpoints:
  /analytics/source-distribution  → publisher coverage
  /analytics/category-distribution → keyword distribution

To change the keyword set, edit app/scraper/keywords.py.
"""

from app.scraper.base import ScrapedArticle
from app.scraper.keywords import HEALTHCARE_KEYWORDS
from app.scraper.rss import GoogleNewsRSSScraper


def get_all_scrapers() -> list[GoogleNewsRSSScraper]:
    """Return one initialised RSS scraper per healthcare keyword."""
    return [GoogleNewsRSSScraper(keyword) for keyword in HEALTHCARE_KEYWORDS]


def get_scraper(keyword: str) -> GoogleNewsRSSScraper:
    """Return an initialised scraper for *keyword*, or raise ValueError."""
    if keyword not in HEALTHCARE_KEYWORDS:
        raise ValueError(
            f"Unknown keyword {keyword!r}. "
            f"Valid keywords: {HEALTHCARE_KEYWORDS}"
        )
    return GoogleNewsRSSScraper(keyword)


__all__ = [
    "ScrapedArticle",
    "GoogleNewsRSSScraper",
    "HEALTHCARE_KEYWORDS",
    "get_all_scrapers",
    "get_scraper",
]
