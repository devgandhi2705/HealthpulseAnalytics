"""
Production entry point — Hugging Face Spaces & Docker.

Named server.py (not app.py) to avoid a Python module naming conflict:
the backend package is also called 'app' (backend/app/), so a root-level
app.py would shadow it when Python resolves 'from app.main import app'.

Start with:
    uvicorn server:app --host 0.0.0.0 --port 7860
"""

import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — make backend/app importable as the 'app' package
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent
_BACKEND = _ROOT / "backend"
sys.path.insert(0, str(_BACKEND))

# Tell the backend where to find the pre-built React app.
_DIST = _ROOT / "frontend" / "dist"
if _DIST.exists() and not os.getenv("FRONTEND_DIST"):
    os.environ["FRONTEND_DIST"] = str(_DIST)

# ---------------------------------------------------------------------------
# Import FastAPI application
# 'app' here resolves to backend/app/ (not this file) because sys.path
# now has backend/ at position 0 and this file is server.py, not app.py.
# ---------------------------------------------------------------------------
from app.main import app  # noqa: E402  # type: ignore[import]

logging.getLogger(__name__).info(
    "HealthPulse Analytics starting on port %s",
    os.getenv("PORT", "7860"),
)
