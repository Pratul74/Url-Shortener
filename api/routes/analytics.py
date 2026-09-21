import uuid
from datetime import date

from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db import db_dependency
from services import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/{url_id}/dashboard")
async def get_analytics_dashboard(
    db: db_dependency,
    url_id: uuid.UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    target_date: date = Query(...),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    limit: int = Query(3, ge=1, le=50)
):
    service = AnalyticsService(db)
    return await service.get_analytics_dashboard(
        url_id=url_id,
        start_date=start_date,
        end_date=end_date,
        target_date=target_date,
        month=month,
        year=year,
        limit=limit,
    )
