"""
Production entry point — Hugging Face Spaces & Docker.

Adds the backend package to sys.path, then re-exports the FastAPI `app`
object so uvicorn can be invoked as:

    uvicorn app:app --host 0.0.0.0 --port 7860

The React frontend is served as static files from frontend/dist/ if the
build artefacts are present.  Run `cd frontend && npm run build` first, or
let the Dockerfile handle it automatically.
"""

import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent
_BACKEND = _ROOT / "backend"
sys.path.insert(0, str(_BACKEND))

# Tell the backend where to find the pre-built React app.
_DIST = _ROOT / "frontend" / "dist"
if _DIST.exists() and not os.getenv("FRONTEND_DIST"):
    os.environ["FRONTEND_DIST"] = str(_DIST)

# ---------------------------------------------------------------------------
# Import FastAPI application (triggers DB init via lifespan on first request)
# ---------------------------------------------------------------------------
from app.main import app  # noqa: E402

logging.getLogger(__name__).info(
    "HealthPulse Analytics starting on port %s",
    os.getenv("PORT", "7860"),
)
