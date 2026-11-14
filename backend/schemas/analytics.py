from pydantic import BaseModel
from typing import Optional

class CreateAnalytics(BaseModel):
    url_id: int
    ip_address: str
    country: Optional[str] = None
    city: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: str

class AnalyticsOut(BaseModel):
    url_id: str
    total_clicks: int
    country: dict[str, int]
    city: dict[str, int]
    browser: dict[str, int]
    os: dict[str, int]
    device: dict[str, int]
    referrer: dict[str, int]