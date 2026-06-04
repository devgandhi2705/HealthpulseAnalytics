import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ------------------------------------------------------------------
# Retry policy
# ------------------------------------------------------------------
# 3 attempts total, exponential back-off: 0 s, 1.5 s, 3 s.
# Only retries on transient server-side and rate-limit status codes.
_RETRY_TOTAL = 3
_RETRY_BACKOFF_FACTOR = 1.5
_RETRY_ON_STATUS = frozenset([429, 500, 502, 503, 504])


def build_session() -> requests.Session:
    """
    Return a requests.Session pre-configured with:
      - Automatic retries with exponential back-off
      - A descriptive User-Agent (some sources block the default)
      - Standard browser-like Accept headers
    """
    retry_policy = Retry(
        total=_RETRY_TOTAL,
        backoff_factor=_RETRY_BACKOFF_FACTOR,
        status_forcelist=list(_RETRY_ON_STATUS),
        allowed_methods=["GET"],
        raise_on_status=False,  # let callers inspect the response themselves
    )
    adapter = HTTPAdapter(max_retries=retry_policy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (compatible; HealthPulse-Analytics/1.0; "
                "health research aggregator)"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
        }
    )
    return session
