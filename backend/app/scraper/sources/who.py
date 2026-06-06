from datetime import datetime
import logging
from typing import Optional

from bs4 import BeautifulSoup

from app.scraper.base import BaseScraper, ScrapedArticle

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# CSS selectors
# ------------------------------------------------------------------
# Update these if WHO redesigns their news listing page.
# Inspect https://www.who.int/news to verify current structure.

_NEWS_URL = "https://www.who.int/news"
_ARTICLE_CONTAINER = "li.sf-list-vertical__item"
_TITLE_LINK = ".sf-list-vertical__title a"
_DATE_SPAN = "span.timestamp__time"

# WHO publishes dates in "22 May 2025" format.
_DATE_FORMAT = "%d %B %Y"


class WHOScraper(BaseScraper):
    """
    Scrapes the WHO latest-news listing page.

    Source  : https://www.who.int/news
    Category: policy  (WHO publishes policy, outbreak, and research items;
              the category field can be refined per-article later via NLP)
    """

    SOURCE_NAME = "WHO"
    DEFAULT_CATEGORY = "policy"
    BASE_URL = _NEWS_URL

    def scrape(self) -> list[ScrapedArticle]:
        self.logger.info("[%s] Fetching %s", self.SOURCE_NAME, self.BASE_URL)

        html = self._fetch(self.BASE_URL)

        if html is None:
            self.logger.warning(
                "[%s] FETCH FAILED | status=%s | url=%s",
                self.SOURCE_NAME,
                self._last_http_status or "network_error",
                self.BASE_URL,
            )
            return []

        self.logger.info(
            "[%s] Fetch OK    | status=%d | size=%s bytes",
            self.SOURCE_NAME,
            self._last_http_status,
            f"{self._last_response_bytes:,}",
        )

        articles = self._parse(html)

        skipped = self._last_cards_found - len(articles)
        self.logger.info(
            "[%s] ── Summary ── status=%-3d | size=%-10s | cards=%-3d | extracted=%-3d%s",
            self.SOURCE_NAME,
            self._last_http_status or 0,
            f"{self._last_response_bytes:,}",
            self._last_cards_found,
            len(articles),
            f" | skipped={skipped}" if skipped > 0 else "",
        )
        return articles

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse(self, html: str) -> list[ScrapedArticle]:
        soup = BeautifulSoup(html, "html.parser")
        containers = soup.select(_ARTICLE_CONTAINER)
        self._last_cards_found = len(containers)

        self.logger.debug(
            "[%s] Selector %r matched %d element(s)",
            self.SOURCE_NAME, _ARTICLE_CONTAINER, len(containers),
        )

        if not containers:
            page_title = (
                soup.title.string.strip()
                if soup.title and soup.title.string
                else "(no <title>)"
            )
            self.logger.warning(
                "[%s] ZERO CARDS — selector %r returned nothing. "
                "Page title: %r  (page structure may have changed or request was blocked)",
                self.SOURCE_NAME, _ARTICLE_CONTAINER, page_title,
            )

        results: list[ScrapedArticle] = []
        for item in containers:
            article = self._parse_item(item)
            if article is not None:
                results.append(article)
        return results

    def _parse_item(self, item: BeautifulSoup) -> Optional[ScrapedArticle]:
        title, url = self._extract_title_and_url(item)
        if not title or not url:
            return None

        return ScrapedArticle(
            title=title,
            url=url,
            source=self.SOURCE_NAME,
            category=self.DEFAULT_CATEGORY,
            published_date=self._extract_date(item),
            article_text=self._fetch_article_text(url),
        )

    def _extract_title_and_url(
        self, item: BeautifulSoup
    ) -> tuple[Optional[str], Optional[str]]:
        link_tag = item.select_one(_TITLE_LINK)
        if link_tag is None:
            self.logger.debug("No title link found in item: %s", item)
            return None, None

        title = link_tag.get_text(strip=True)
        href = link_tag.get("href", "")

        # WHO hrefs are relative paths — prepend the origin.
        if href.startswith("/"):
            href = f"https://www.who.int{href}"

        return (title or None, href or None)

    def _extract_date(self, item: BeautifulSoup) -> Optional[datetime]:
        span = item.select_one(_DATE_SPAN)
        if span is None:
            return None

        raw = span.get_text(strip=True)
        return _parse_who_date(raw)


def _parse_who_date(raw: str) -> Optional[datetime]:
    """
    Parse a WHO date string such as "22 May 2025".
    Returns None if the string cannot be parsed rather than raising.
    """
    try:
        return datetime.strptime(raw.strip(), _DATE_FORMAT)
    except ValueError:
        logger.debug("Could not parse date string %r with format %r", raw, _DATE_FORMAT)
        return None
