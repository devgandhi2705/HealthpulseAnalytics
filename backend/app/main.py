import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.database.init_db import init_db

# ---------------------------------------------------------------------------
# Logging — configure once at import time so all loggers inherit the format.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting HealthPulse Analytics API …")
    init_db()
    logger.info("Startup complete — API is ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="HealthPulse Analytics",
    description="API for health data aggregation and analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — origins are read from the environment so production deployments
# can restrict access without code changes.
# Set CORS_ORIGINS to a comma-separated list, e.g.:
#   CORS_ORIGINS=https://myapp.com,https://staging.myapp.com
# Leave unset to allow the default local development origins.
# ---------------------------------------------------------------------------
_raw_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:7860,http://127.0.0.1:7860",
)
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# ---------------------------------------------------------------------------
# Static file serving — mount the pre-built React frontend if available.
# Set FRONTEND_DIST to the absolute path of the Vite build output directory,
# or leave unset to auto-detect <repo_root>/frontend/dist.
# ---------------------------------------------------------------------------
_dist_env = os.getenv("FRONTEND_DIST", "")
_dist = Path(_dist_env) if _dist_env else Path(__file__).resolve().parents[2] / "frontend" / "dist"

if _dist.exists():
    from fastapi.responses import FileResponse  # noqa: E402
    from fastapi.staticfiles import StaticFiles  # noqa: E402

    # Serve Vite's JS/CSS chunks from /assets — registered AFTER the API router
    # so no API path can ever be shadowed.
    _assets = _dist / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="vite-assets")

    # Catch-all for SPA client-side routes (e.g. /articles, /dashboard).
    # Because this is added after app.include_router(router), every real API
    # route is matched first; only truly unmatched paths reach here.
    @app.get("/{full_path:path}", include_in_schema=False)
    async def _spa(full_path: str):  # noqa: F811
        return FileResponse(str(_dist / "index.html"))

    logger.info("Serving frontend static files from %s", _dist)
