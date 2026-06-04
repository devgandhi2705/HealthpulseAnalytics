from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all SQLAlchemy models.

    All model classes must inherit from this Base so that
    Alembic migrations and table creation can discover them
    from a single registry.
    """
    pass
