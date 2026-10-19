from fastapi import APIRouter, BackgroundTasks, Request, status
from fastapi.responses import RedirectResponse
from services import UrlShortenerService
from db import db_dependency
import logging
from messaging.events import ClickEvent
from datetime import datetime, timezone
from messaging import click_event_producer

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{short_code}")
async def get_original_url(db: db_dependency, short_code: str, request: Request, background_tasks: BackgroundTasks):
    url_service = UrlShortenerService(db)
    url = await url_service.get_original_url(short_code)

    background_tasks.add_task(
        publish_event,
        ClickEvent(
            url_id = int(url.id),
            short_code=url.short_code,
            ip=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", ""),
            referrer=request.headers.get("referer", ""),
            timestamp=datetime.now(timezone.utc),
        )
    )
    return RedirectResponse(url=url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

async def publish_event(click_event: ClickEvent):
    try:
        await click_event_producer.publish(click_event)
    except Exception:
        logger.exception("Failed to publish click event")