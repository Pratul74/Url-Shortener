from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import Literal

class ClickEvent(BaseModel):
    url_id: int
    short_code: str
    ip: str
    user_agent: str
    referrer: Optional[str] = None
    timestamp: datetime

class QrCodeJobEvent(BaseModel):
    short_code: str
    actions : Literal["generate", "delete"] = "generate"
    