import os
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["system"])

# Resolve the pre-built React index.html.  FRONTEND_DIST can be set in the
# environment to override the default <repo_root>/frontend/dist location.
_dist_env = os.getenv("FRONTEND_DIST", "")
_index = (
    Path(_dist_env) / "index.html"
    if _dist_env
    else Path(__file__).resolve().parents[3] / "frontend" / "dist" / "index.html"
)


@router.get("/", include_in_schema=False)
def root():
    """Serve the React dashboard in production; return API info otherwise."""
    if _index.exists():
        return FileResponse(str(_index))
    return {"message": "HealthPulse Analytics API", "version": "1.0.0"}


@router.get("/health")
def health_check():
    return {"status": "ok"}
