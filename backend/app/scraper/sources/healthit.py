import logging
from typing import Optional

from bs4 import BeautifulSoup, Tag

from app.scraper.base import BaseScraper, ScrapedArticle, parse_date

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Selectors
# ---------------------------------------------------------------------------
# HealthIT.gov (ONC) hosts its primary news content on the Buzz Blog.
# If this scraper returns 0 results, inspect the live page and update below.
# Live page: https://www.healthit.gov/buzz-blog

_NEWS_URL   = "https://www.healthit.gov/buzz-blog"
_ORIGIN     = "https://www.healthit.gov"

# The blog uses either article elements or Drupal views rows.
_CONTAINER  = "article, .blog-post, li.views-row, .view-content .views-row"

# Title/link inside each post card.
_TITLE_LINK = "h2 a, h3 a, .entry-title a, .views-field-title a, .node-title a"

# Date element.
_DATE_SEL   = "time[datetime], .entry-date, .views-field-created span, span.date, .post-date"


class HealthITScraper(BaseScraper):
    """
    Scrapes the ONC / HealthIT.gov Buzz Blog.

    Source  : https://www.healthit.gov/buzz-blog
    Category: health-it
    """

    SOURCE_NAME      = "HealthIT.gov"
    DEFAULT_CATEGORY = "health-it"
    BASE_URL         = _NEWS_URL

    def scrape(self) -> list[ScrapedArticle]:
        self.logger.info("Scraping %s", self.BASE_URL)
        html = self._fetch(self.BASE_URL)
        if html is None:
            return []
        articles = self._parse(html)
        self.logger.info("Found %d articles from %s", len(articles), self.SOURCE_NAME)
        return articles

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse(self, html: str) -> list[ScrapedArticle]:
        soup       = BeautifulSoup(html, "html.parser")
        containers = soup.select(_CONTAINER)

        if not containers:
            self.logger.warning(
                "No containers matched %r — HealthIT.gov page structure may have changed.",
                _CONTAINER,
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
        # Check <time datetime="..."> first — most modern sites use this.
        time_tag = item.select_one("time[datetime]")
        if time_tag:
            parsed = parse_date(time_tag.get("datetime", ""))
            if parsed:
                return parsed

        date_tag = item.select_one(_DATE_SEL)
        if date_tag:
            return parse_date(date_tag.get_text(strip=True))
        return None
