from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.base import Base


class Article(Base):
    """
    Represents a single scraped healthcare news article.

    url is the natural unique key — the scraper uses it to avoid
    inserting duplicates before hitting the database constraint.
    """

    __tablename__ = "articles"

    # ------------------------------------------------------------------
    # Primary key
    # ------------------------------------------------------------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ------------------------------------------------------------------
    # Content fields
    # ------------------------------------------------------------------
    title: Mapped[str] = mapped_column(String(512), nullable=False)

    # Name of the outlet / feed (e.g. "WHO", "CDC", "Reuters Health")
    source: Mapped[str] = mapped_column(String(255), nullable=False)

    # Broad topic bucket (e.g. "research", "policy", "outbreak")
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    # Short plain-text excerpt or AI-generated summary; nullable because
    # some sources publish headline-only items.
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Full cleaned body text extracted from the article detail page.
    # Nullable: content fetch may fail or the page may be paywalled.
    article_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Canonical article URL — unique constraint prevents duplicate rows.
    url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # ------------------------------------------------------------------
    # Temporal fields
    # ------------------------------------------------------------------

    # Date/time the article was originally published by the source.
    # Nullable: not all feeds expose a publication date.
    published_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Date/time the scraper collected this record.
    # Set explicitly by the scraper rather than defaulting to created_at
    # so batch back-fills can carry the correct collection timestamp.
    scraped_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Immutable record-creation timestamp set automatically by the DB.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------
    # Constraints and indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        # Enforce uniqueness at the DB level as a safety net.
        UniqueConstraint("url", name="uq_articles_url"),
        # Single-column indexes for common filter columns.
        Index("ix_articles_source", "source"),
        Index("ix_articles_category", "category"),
        Index("ix_articles_published_date", "published_date"),
        # Composite index for the most common dashboard query:
        # "all articles in category X ordered by date".
        Index("ix_articles_category_published_date", "category", "published_date"),
    )

    def __repr__(self) -> str:
        return f"<Article id={self.id} source={self.source!r} title={self.title[:40]!r}>"
