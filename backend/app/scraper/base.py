from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Shared date parser
# ---------------------------------------------------------------------------
# Formats are tried in order; the first match wins.
# Add new patterns at the top when a source uses an unusual format.

_DATE_FORMATS = [
    "%B %d, %Y",          # "March 14, 2025"
    "%b %d, %Y",          # "Mar 14, 2025"
    "%b. %d, %Y",         # "Mar. 14, 2025"
    "%Y-%m-%d",           # "2025-03-14"      (ISO date)
    "%Y-%m-%dT%H:%M:%S",  # "2025-03-14T10:30:00"
    "%Y-%m-%dT%H:%M:%SZ", # "2025-03-14T10:30:00Z"
    "%m/%d/%Y",           # "03/14/2025"
    "%d %B %Y",           # "14 March 2025"   (WHO style)
]

_date_logger = logging.getLogger("scraper.parse_date")


def parse_date(raw: str) -> Optional[datetime]:
    """
    Try every format in _DATE_FORMATS against *raw*.
    Returns None on failure rather than raising so callers stay clean.
    Normalises internal whitespace before attempting each parse.
    """
    if not raw:
        return None
    raw = " ".join(raw.strip().split())
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    _date_logger.debug("Could not parse date string %r", raw)
    return None


@dataclass
class ScrapedArticle:
    """
    Normalised article data returned by every scraper.

    All scrapers produce this type so the rest of the system
    never needs to know which source the data came from.
    """

    title: str
    url: str
    source: str           # matches BaseScraper.SOURCE_NAME
    category: str         # broad topic bucket, e.g. "policy", "research"
    published_date: Optional[datetime]
    summary: Optional[str] = field(default=None)
    # Full cleaned body text fetched from the article detail page.
    article_text: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.url = self.url.strip()


class BaseScraper(ABC):
    """
    Contract that every source-specific scraper must fulfil.

    Subclasses must declare SOURCE_NAME and DEFAULT_CATEGORY as
    class-level constants, then implement scrape().

    The shared _fetch() method handles timeouts and logs errors
    so individual scrapers only contain parsing logic.
    """

    SOURCE_NAME: str = ""        # human-readable source identifier
    DEFAULT_CATEGORY: str = "general"
    BASE_URL: str = ""           # seed URL scraped by this source

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.logger = logging.getLogger(f"scraper.{self.SOURCE_NAME}")
        self._session = session
        # Populated by _fetch() so subclasses can include them in log summaries.
        self._last_http_status: Optional[int] = None
        self._last_response_bytes: int = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @abstractmethod
    def scrape(self) -> list[ScrapedArticle]:
        """Fetch the source and return a list of normalised articles."""
        ...

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            from app.scraper.http_client import build_session
            self._session = build_session()
        return self._session

    def _fetch(self, url: str, timeout: int = 15) -> Optional[str]:
        """
        GET *url* and return the response body as a string.

        Returns None on any network or HTTP error so callers can
        decide whether to skip silently or raise.

        Side-effects: sets self._last_http_status and
        self._last_response_bytes so subclasses can include them in
        their scrape-summary log without re-fetching.
        """
        self._last_http_status = None
        self._last_response_bytes = 0
        try:
            response = self.session.get(url, timeout=timeout)
            self._last_http_status = response.status_code
            self._last_response_bytes = len(response.content)
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            self.logger.error("Timeout fetching %s", url)
        except requests.exceptions.HTTPError as exc:
            self._last_http_status = exc.response.status_code
            self.logger.error("HTTP %s for %s", exc.response.status_code, url)
        except requests.exceptions.RequestException as exc:
            self.logger.error("Request failed for %s: %s", url, exc)
        return None

    def _fetch_article_text(self, url: str) -> Optional[str]:
        """
        Fetch and return the cleaned full-text body from the article detail
        page at *url*.  Returns None on any failure so a missing article body
        never aborts the listing scrape.
        """
        from app.scraper.content import extract_article_text  # lazy to avoid circular import
        return extract_article_text(url, self.session)
