from __future__ import annotations

from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.api.schemas.article import ArticleResponse, PaginatedResponse
from app.database.session import get_db
from app.models.article import Article

router = APIRouter(prefix="/articles", tags=["articles"])

# ---------------------------------------------------------------------------
# Reusable query-parameter types
# ---------------------------------------------------------------------------

PageParam = Annotated[int, Query(ge=1, description="Page number (1-indexed)")]
PageSizeParam = Annotated[int, Query(ge=1, le=100, description="Items per page (max 100)")]

SortByParam = Annotated[
    Literal["published_date", "scraped_date", "created_at"],
    Query(description="Field to sort by"),
]
SortOrderParam = Annotated[
    Literal["asc", "desc"],
    Query(description="Sort direction"),
]

# Maps the sort_by string to the ORM column used in ORDER BY.
_SORT_COLUMNS = {
    "published_date": Article.published_date,
    "scraped_date": Article.scraped_date,
    "created_at": Article.created_at,
}


# ---------------------------------------------------------------------------
# GET /articles
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=PaginatedResponse[ArticleResponse],
    summary="List articles",
)
def list_articles(
    page: PageParam = 1,
    page_size: PageSizeParam = 20,
    source: Annotated[Optional[str], Query(description="Filter by source name")] = None,
    category: Annotated[Optional[str], Query(description="Filter by category")] = None,
    sort_by: SortByParam = "published_date",
    sort_order: SortOrderParam = "desc",
    db: Session = Depends(get_db),
) -> PaginatedResponse[ArticleResponse]:
    """
    Return a paginated list of articles.

    Supports optional filtering by **source** and **category**, and sorting
    by any timestamp column.  Filters are case-insensitive substring matches.
    """
    query = _base_query(db, source=source, category=category)
    query = _apply_sort(query, sort_by=sort_by, sort_order=sort_order)
    return _paginate(query, page=page, page_size=page_size)


# ---------------------------------------------------------------------------
# GET /articles/search
# NOTE: defined before /{id} so "search" is not swallowed as an integer id.
# ---------------------------------------------------------------------------

@router.get(
    "/search",
    response_model=PaginatedResponse[ArticleResponse],
    summary="Search articles by title",
)
def search_articles(
    q: Annotated[str, Query(min_length=1, description="Search term (title match)")],
    page: PageParam = 1,
    page_size: PageSizeParam = 20,
    source: Annotated[Optional[str], Query(description="Filter by source name")] = None,
    category: Annotated[Optional[str], Query(description="Filter by category")] = None,
    sort_by: SortByParam = "published_date",
    sort_order: SortOrderParam = "desc",
    db: Session = Depends(get_db),
) -> PaginatedResponse[ArticleResponse]:
    """
    Full-text search across article **titles**.

    Combines seamlessly with source/category filters and pagination.
    The search is case-insensitive and matches partial words.
    """
    query = _base_query(db, source=source, category=category)
    query = query.filter(Article.title.ilike(f"%{q}%"))
    query = _apply_sort(query, sort_by=sort_by, sort_order=sort_order)
    return _paginate(query, page=page, page_size=page_size)


# ---------------------------------------------------------------------------
# GET /articles/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="Get a single article",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Article not found"},
    },
)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleResponse:
    """Return the article with the given **id**, or 404 if it does not exist."""
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article {article_id} not found.",
        )
    return article  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _base_query(
    db: Session,
    source: Optional[str],
    category: Optional[str],
):
    """Return a Query pre-filtered by source and category (when provided)."""
    q = db.query(Article)
    if source:
        q = q.filter(Article.source.ilike(f"%{source}%"))
    if category:
        q = q.filter(Article.category.ilike(f"%{category}%"))
    return q


def _apply_sort(query, sort_by: str, sort_order: str):
    """Attach an ORDER BY clause to *query*."""
    column = _SORT_COLUMNS[sort_by]
    direction = desc if sort_order == "desc" else asc
    # NULLs (e.g. missing published_date) always go last regardless of direction.
    return query.order_by(direction(column).nulls_last())


def _paginate(
    query,
    page: int,
    page_size: int,
) -> PaginatedResponse[ArticleResponse]:
    """Count, slice, and wrap *query* results in a PaginatedResponse."""
    total: int = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
