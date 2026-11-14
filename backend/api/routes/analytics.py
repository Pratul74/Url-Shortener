from typing import Annotated

from fastapi import APIRouter, Path
from backend.db import db_dependency
from backend.dependencies import CurrentUser
from backend.services import AnalyticsService
from backend.schemas import AnalyticsOut

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/{url_id}/dashboard", response_model=AnalyticsOut)
async def get_dashboard(
    url_id: Annotated[int, Path(ge=0, le=2**63 - 1)],
    db: db_dependency, user: CurrentUser):
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