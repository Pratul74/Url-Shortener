from fastapi import APIRouter
from .routes import url_router

router = APIRouter()

router.include_router(url_router)