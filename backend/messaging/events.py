from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import StrEnum

class ClickEvent(BaseModel):
    url_id: int
    short_code: str
    ip: str
    user_agent: str
    referrer: Optional[str] = None
    timestamp: datetime

class QrAction(StrEnum):
    DELETE = "delete"
    UPLOAD = "upload"

class QrCodeJobEvent(BaseModel):
    short_code: str
    action : QrAction
    qr_key: str | None = None
    