from fastapi import APIRouter

from app.api.analytics import router as analytics_router
from app.api.articles import router as articles_router
from app.api.eda import router as eda_router
from app.api.health import router as health_router
from app.api.scrape import router as scrape_router
from app.api.sql_analytics import router as sql_analytics_router
from app.api.system import router as system_router

router = APIRouter()
router.include_router(health_router)
router.include_router(system_router)
router.include_router(articles_router)
router.include_router(analytics_router)
router.include_router(eda_router)
router.include_router(scrape_router)
router.include_router(sql_analytics_router)
