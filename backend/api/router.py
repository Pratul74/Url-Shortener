from fastapi import APIRouter
from .routes import url_router, auth_router, analytics_router

router = APIRouter()

router.include_router(url_router)
router.include_router(auth_router)
router.include_router(analytics_router)
