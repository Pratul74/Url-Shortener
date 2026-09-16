from pydantic import BaseModel
import uuid
from typing import Optional

class Country(BaseModel):
    country: str
    click_count: int


class City(BaseModel):
    city:str
    click_count:int

class Browser(BaseModel):
    browser: str
    click_count: int

class Device(BaseModel):
    device: str
    click_count: int

class Os(BaseModel):
    os: str
    click_count: int

class Ip(BaseModel):
    ip_address: str
    click_count: int

class CreateAnalytics(BaseModel):
    url_id: uuid.UUID
    ip_address: str
    country: Optional[str] = None
    city: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: str
