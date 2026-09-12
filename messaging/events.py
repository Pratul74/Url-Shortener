from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClickEvent(BaseModel):
    url_id: str
    short_code: str
    ip: str
    user_agent: str
    referrer: Optional[str] = None
    timestamp: datetime
    