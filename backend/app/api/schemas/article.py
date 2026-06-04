from __future__ import annotations

import math
from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ArticleResponse(BaseModel):
    """API representation of a single stored article."""

    id: int
    title: str
    source: str
    category: str
    summary: Optional[str]
    url: str
    published_date: Optional[datetime]
    scraped_date: datetime
    created_at: datetime

    # Populate from ORM attributes directly (replaces orm_mode=True in v1).
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic envelope for any paginated list endpoint.

    Usage:
        response_model=PaginatedResponse[ArticleResponse]
    """

    items: list[T]
    total: int = Field(description="Total matching records across all pages")
    page: int = Field(description="Current page (1-indexed)")
    page_size: int = Field(description="Maximum items returned per page")
    pages: int = Field(description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[T]:
        pages = math.ceil(total / page_size) if page_size else 0
        return cls(items=items, total=total, page=page, page_size=page_size, pages=pages)
