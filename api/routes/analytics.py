from fastapi import APIRouter
import uuid
from db import db_dependency
from dependencies import CurrentUser
from services import AnalyticsService
from schemas import AnalyticsOut

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/{url_id}/dashboard", response_model=AnalyticsOut)
async def get_dashboard(url_id: uuid.UUID, db: db_dependency, user: CurrentUser):
    service = AnalyticsService(db)
    return await service.get_analytics(user_id=user.id, url_id=url_id)