import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.article import Article

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system"])


@router.get(
    "/system/status",
    summary="Check database readiness and article count",
)
def get_system_status(db: Session = Depends(get_db)) -> dict:
    total = db.query(func.count(Article.id)).scalar() or 0
    return {
        "database_initialized": True,
        "total_articles": total,
    }
