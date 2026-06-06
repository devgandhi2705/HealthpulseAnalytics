import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------
# Priority (highest → lowest):
#   1. DATABASE_URL env var  — any dialect (SQLite, PostgreSQL, …)
#   2. /data/healthpulse.db  — HuggingFace Spaces persistent volume (SPACE_ID is set)
#   3. backend/data/healthpulse.db — local development fallback

def _default_sqlite_url() -> str:
    # HF Spaces sets SPACE_ID; /data is the persistent storage mount point.
    db_path = (
        Path("/data/healthpulse.db")
        if os.getenv("SPACE_ID")
        else Path(__file__).resolve().parents[2] / "data" / "healthpulse.db"
    )
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"

DATABASE_URL: str = os.getenv("DATABASE_URL") or _default_sqlite_url()

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# check_same_thread=False is required for SQLite when used with FastAPI's
# async request handling (multiple threads share one connection).
# This argument is silently ignored by other dialects (e.g. PostgreSQL).

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    # Pool size tuning is a no-op for SQLite but takes effect on PostgreSQL.
    pool_pre_ping=True,  # recycle stale connections automatically
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# autocommit=False  — explicit commits required (safe default)
# autoflush=False   — prevent implicit flushes before every query

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session for the duration of a single request,
    then close it automatically — even if the handler raises.

    Usage in a route:
        from app.database.session import get_db
        ...
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
