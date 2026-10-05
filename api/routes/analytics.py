from fastapi import APIRouter
from db import db_dependency
from dependencies import CurrentUser
from services import AnalyticsService
from schemas import AnalyticsOut

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/{url_id}/dashboard", response_model=AnalyticsOut)
async def get_dashboard(url_id: int, db: db_dependency, user: CurrentUser):
    service = AnalyticsService(db)
    dashboard = await service.get_analytics(user_id=user.id, url_id=url_id)
    return AnalyticsOut(
        url_id=str(dashboard['url_id']),
        total_clicks=dashboard['total_clicks'],
        country=dashboard['country'],
        city=dashboard['city'],
        browser=dashboard['browser'],
        os=dashboard['os'],
        device=dashboard['device'],
        referrer=dashboard['referrer']
    )