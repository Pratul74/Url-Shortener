from fastapi import APIRouter, BackgroundTasks, Request, status
from fastapi.responses import RedirectResponse
from backend.services import UrlShortenerService
from backend.db import db_dependency
import logging
from backend.messaging.events import ClickEvent
from datetime import datetime, timezone
from backend.messaging import click_event_producer

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{short_code}")
async def get_original_url(db: db_dependency, short_code: str, request: Request, background_tasks: BackgroundTasks):
    url_service = UrlShortenerService(db)
    url = await url_service.get_original_url(short_code)
    ip_address =  request.client.host if request.client else "Unknown"
    logger.info("Click on %s from ip=%s", short_code, ip_address)
    background_tasks.add_task(
        publish_event,
        ClickEvent(
            url_id = int(url.id),
            short_code=url.short_code,
            ip=ip_address,
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