import logging

from sqlalchemy import inspect, text

from app.database.base import Base
from app.database.session import engine

# Side-effect imports: registers each model class with Base so that
# create_all() knows which tables to create.  Add new model modules here
# as the schema grows.
import app.models.article  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Create any missing tables, then apply lightweight column migrations.

    create_all() handles brand-new databases.  _migrate_schema() handles
    databases that already exist but predate a column addition.
    """
    logger.info("Initialising database schema...")
    Base.metadata.create_all(bind=engine)
    _migrate_schema()
    logger.info("Database schema ready.")


def _migrate_schema() -> None:
    """
    Add columns that exist in the ORM model but are absent from the live table.

    Uses SQLAlchemy's Inspector so the same code works for SQLite and
    PostgreSQL.  Each ALTER TABLE is idempotent — safe to call on every
    startup.
    """
    inspector = inspect(engine)

    if not inspector.has_table("articles"):
        return  # table was just created by create_all with all columns

    existing = {col["name"] for col in inspector.get_columns("articles")}

    migrations: list[str] = []
    if "article_text" not in existing:
        migrations.append("ALTER TABLE articles ADD COLUMN article_text TEXT")

    if not migrations:
        return

    with engine.connect() as conn:
        for stmt in migrations:
            conn.execute(text(stmt))
            logger.info("Migration applied: %s", stmt)
        conn.commit()
