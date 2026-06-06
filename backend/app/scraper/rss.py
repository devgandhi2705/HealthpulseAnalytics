"""
Google News RSS scraper.

One instance per keyword.  Fetches the Google News RSS search feed,
parses items with the stdlib XML parser, and maps them onto the shared
ScrapedArticle dataclass so the rest of the pipeline is unchanged.

Schema mapping
--------------
  ScrapedArticle.source   → publisher name  (e.g. "Reuters", "The Guardian")
  ScrapedArticle.category → search keyword  (e.g. "healthcare", "telemedicine")

This keeps every existing analytics endpoint valid because the DB columns
source/category are already used for distribution queries.
"""

import html
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional
from urllib.parse import quote_plus

import requests

from app.scraper.base import ScrapedArticle

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_RSS_BASE = "https://news.google.com/rss/search"
_RSS_PARAMS = "hl=en-US&gl=US&ceid=US:en"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")

# Google News appends " - Publisher" or " – Publisher" to titles.
# We try these separators right-to-left so the last occurrence wins.
_TITLE_SEPS = [" – ", " — ", " - "]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    """Decode HTML entities, strip tags, normalise whitespace."""
    text = html.unescape(text or "")
    text = _HTML_TAG_RE.sub(" ", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def _parse_date(raw: str) -> Optional[datetime]:
    """Parse RFC 2822 date string into a naive UTC datetime."""
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw.strip())
        return dt.replace(tzinfo=None)
    except Exception:
        return None


def _get_url(item: ET.Element) -> str:
    """
    Return the best article URL from an RSS <item>.

    Google News RSS writes the redirect URL as the text of <link>.
    If that is absent or blank, fall back to <guid>.
    """
    link = (item.findtext("link") or "").strip()
    if link.startswith("http"):
        return link
    guid = (item.findtext("guid") or "").strip()
    return guid if guid.startswith("http") else ""


def _split_title_publisher(raw_title: str) -> tuple[str, str]:
    """
    Split "Article headline – Publisher Name" into (headline, publisher).
    Returns (raw_title, "") when no separator is found.
    """
    for sep in _TITLE_SEPS:
        if sep in raw_title:
            parts = raw_title.rsplit(sep, 1)
            candidate = parts[1].strip()
            # Sanity-check: publisher names are short
            if candidate and len(candidate) < 80:
                return parts[0].strip(), candidate
    return raw_title, ""


# ---------------------------------------------------------------------------
# Scraper class
# ---------------------------------------------------------------------------

class GoogleNewsRSSScraper:
    """
    Fetches Google News RSS for a single keyword and returns
    a list[ScrapedArticle] ready for the ingestion pipeline.
    """

    SOURCE_NAME = "GoogleNews"

    def __init__(
        self,
        keyword: str,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.keyword = keyword
        self._session = session or requests.Session()
        self._session.headers.update(_HEADERS)
        self.logger = logging.getLogger(
            "scraper.rss.{}".format(keyword.replace(" ", "_"))
        )

        # Diagnostic attributes mirror BaseScraper conventions
        self._last_http_status: Optional[int] = None
        self._last_response_bytes: int = 0
        self._last_cards_found: int = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[ScrapedArticle]:
        url = f"{_RSS_BASE}?q={quote_plus(self.keyword)}&{_RSS_PARAMS}"
        self.logger.info("[%s] Fetching %s", self.keyword, url)

        try:
            resp = self._session.get(url, timeout=20)
            self._last_http_status = resp.status_code
            self._last_response_bytes = len(resp.content)
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            self.logger.warning(
                "[%s] FETCH FAILED | status=%s | %s",
                self.keyword,
                self._last_http_status or "network_error",
                exc,
            )
            return []

        self.logger.info(
            "[%s] Fetch OK | status=%d | size=%s bytes",
            self.keyword,
            self._last_http_status,
            f"{self._last_response_bytes:,}",
        )

        articles = self._parse_feed(resp.text)
        skipped = self._last_cards_found - len(articles)
        self.logger.info(
            "[%s] Summary | cards=%-3d | extracted=%-3d%s",
            self.keyword,
            self._last_cards_found,
            len(articles),
            f" | skipped={skipped}" if skipped else "",
        )
        return articles

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_feed(self, xml_text: str) -> list[ScrapedArticle]:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            self.logger.error("[%s] XML parse error: %s", self.keyword, exc)
            return []

        items = root.findall(".//item")
        self._last_cards_found = len(items)

        if not items:
            self.logger.warning("[%s] Feed returned 0 items", self.keyword)

        results: list[ScrapedArticle] = []
        for item in items:
            article = self._parse_item(item)
            if article is not None:
                results.append(article)
        return results

    def _parse_item(self, item: ET.Element) -> Optional[ScrapedArticle]:
        url = _get_url(item)
        raw_title = _clean(item.findtext("title") or "")

        if not url or not raw_title:
            self.logger.debug("[%s] Skipping item — missing url or title", self.keyword)
            return None

        # Publisher: prefer <source> element; fall back to title suffix
        source_el = item.find("source")
        if source_el is not None and (source_el.text or "").strip():
            publisher = source_el.text.strip()
            clean_title = raw_title
        else:
            clean_title, publisher = _split_title_publisher(raw_title)

        if not publisher:
            publisher = "Unknown"

        summary = _clean(item.findtext("description") or "")[:500] or None
        pub_date = _parse_date(item.findtext("pubDate") or "")

        return ScrapedArticle(
            title=clean_title,
            url=url,
            source=publisher,       # maps to Article.source  → publisher
            category=self.keyword,  # maps to Article.category → keyword
            published_date=pub_date,
            summary=summary,
            article_text=None,      # not fetched — avoids paywall issues
        )
