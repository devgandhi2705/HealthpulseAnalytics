import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# ---------------------------------------------------------------------------
# Database URL
# ---------------------------------------------------------------------------
# Default to SQLite for local development.
# Set DATABASE_URL env var to a PostgreSQL DSN (postgresql+psycopg2://...)
# to switch databases without changing any other code.

_BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
_DEFAULT_DB = _BACKEND_DIR / "data" / "healthpulse.db"

# Auto-create the data directory so the app starts on a fresh machine
# without any manual folder creation step.
if not os.getenv("DATABASE_URL"):
    _DEFAULT_DB.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_DB}")

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
