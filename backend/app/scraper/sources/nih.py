import logging
from typing import Optional

from bs4 import BeautifulSoup, Tag

from app.scraper.base import BaseScraper, ScrapedArticle, parse_date

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Selectors
# ---------------------------------------------------------------------------
# NIH.gov runs Drupal 9/10 — the Views module generates these class names.
# If this scraper returns 0 results, inspect the live page and update below.
# Live page: https://www.nih.gov/news-events/news-releases

_NEWS_URL   = "https://www.nih.gov/news-events/news-releases"
_ORIGIN     = "https://www.nih.gov"

# Drupal Views renders each result in a .views-row wrapper.
_CONTAINER  = "div.views-row, article.views-row"

# Title link — Drupal field classes or plain heading anchors.
_TITLE_LINK = ".views-field-title a, h3 a, h2 a"

# Date field — Drupal date formatters output span.date-display-single.
_DATE_SEL   = "span.date-display-single, .views-field-field-date span, time"


class NIHScraper(BaseScraper):
    """
    Scrapes NIH news-release listing.

    Source  : https://www.nih.gov/news-events/news-releases
    Category: research
    """

    SOURCE_NAME      = "NIH"
    DEFAULT_CATEGORY = "research"
    BASE_URL         = _NEWS_URL

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
        soup       = BeautifulSoup(html, "html.parser")
        containers = soup.select(_CONTAINER)
        self._last_cards_found = len(containers)

        self.logger.debug(
            "[%s] Selector %r matched %d element(s)",
            self.SOURCE_NAME, _CONTAINER, len(containers),
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
                self.SOURCE_NAME, _CONTAINER, page_title,
            )

        results: list[ScrapedArticle] = []
        for item in containers:
            article = self._parse_item(item)
            if article is not None:
                results.append(article)
        return results

    def _parse_item(self, item: Tag) -> Optional[ScrapedArticle]:
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

    def _extract_title_and_url(self, item: Tag) -> tuple[Optional[str], Optional[str]]:
        link = item.select_one(_TITLE_LINK)
        if link is None:
            self.logger.debug("No title link in item: %.120s", item)
            return None, None

        title = link.get_text(strip=True) or None
        href  = link.get("href", "") or ""

        if href.startswith("/"):
            href = f"{_ORIGIN}{href}"
        elif not href.startswith("http"):
            href = f"{_ORIGIN}/{href}"

        return title, href or None

    def _extract_date(self, item: Tag) -> Optional[object]:
        time_tag = item.select_one("time[datetime]")
        if time_tag:
            parsed = parse_date(time_tag.get("datetime", ""))
            if parsed:
                return parsed

        date_tag = item.select_one(_DATE_SEL)
        if date_tag:
            return parse_date(date_tag.get_text(strip=True))
        return None
