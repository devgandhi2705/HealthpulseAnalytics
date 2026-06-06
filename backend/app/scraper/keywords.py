"""
Healthcare intelligence keywords.

Each keyword maps to one Google News RSS query.  The scraper fires one
HTTP request per keyword, so the list length directly controls scrape
duration.  Add or remove entries here to adjust coverage.
"""

HEALTHCARE_KEYWORDS: list[str] = [
    "healthcare",
    "public health",
    "hospital",
    "medical research",
    "telemedicine",
    "health insurance",
    "digital health",
    "AI in healthcare",
    "pharmaceutical",
    "disease prevention",
]
