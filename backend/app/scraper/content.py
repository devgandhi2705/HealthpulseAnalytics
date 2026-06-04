import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Content-area selectors
# ---------------------------------------------------------------------------
# Tried in order; the first selector that matches a non-empty element wins.
# Add source-specific selectors at the top for higher priority.

_CONTENT_SELECTORS = [
    ".field-body",              # Drupal (NIH, HealthIT)
    ".page-detail-body",        # WHO
    ".sf-content-block",        # WHO alternate
    ".body-content",
    ".synopsis",                # CDC
    "article .content",
    ".entry-content",           # WordPress
    ".article-body",
    ".post-content",
    ".news-body",
    ".main-content article",
    "main article",
    "article",                  # broad fallback
    "main",                     # last resort
]

# Tags whose text content we want to collect.
_TEXT_TAGS = frozenset({"p", "li", "h2", "h3", "h4", "h5", "blockquote"})

# Tags that are guaranteed not to be part of the article body.
_NOISE_TAGS = frozenset({
    "script", "style", "nav", "header", "footer", "aside",
    "form", "button", "noscript", "iframe", "figure", "figcaption",
})

# Ignore paragraph-like fragments shorter than this — mostly captions /
# navigation labels that slip through the noise removal.
_MIN_PARA_LEN = 30

# Shorter timeout than listing fetches — content is best-effort.
_CONTENT_TIMEOUT = 10


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_article_text(url: str, session: requests.Session) -> Optional[str]:
    """
    Fetch *url*, locate the main article body, strip all HTML, and return
    the text with paragraphs separated by double newlines.

    Returns None on any failure (network error, HTTP error, no parseable
    body) so callers never need to guard against exceptions.
    """
    try:
        response = session.get(url, timeout=_CONTENT_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.debug("Content fetch skipped for %s: %s", url, exc)
        return None

    return _parse_body(response.text, url)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _parse_body(html: str, url: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content structural elements first so their stray text
    # doesn't pollute the paragraph list.
    for noise in soup.find_all(_NOISE_TAGS):
        noise.decompose()

    # Walk selectors until a content block is found.
    content_area = None
    for selector in _CONTENT_SELECTORS:
        content_area = soup.select_one(selector)
        if content_area:
            break

    if content_area is None:
        logger.debug("No content area matched for %s", url)
        return None

    paragraphs: list[str] = []
    for tag in content_area.find_all(_TEXT_TAGS):
        # separator=" " collapses inline child elements (links, em, strong…)
        # into clean readable text rather than running words together.
        text = tag.get_text(separator=" ", strip=True)
        if text and len(text) >= _MIN_PARA_LEN:
            paragraphs.append(text)

    if not paragraphs:
        logger.debug("No usable paragraphs in %s", url)
        return None

    return "\n\n".join(paragraphs)
