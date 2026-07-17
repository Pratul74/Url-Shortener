from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from datetime import datetime

class UrlCreate(BaseModel):
    original_url:HttpUrl
    custom_alias:str | None = Field(
        min_length=3,
        max_length=10,
        default=None
    )

    expires_at:datetime|None = None

class UrlResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:str
    original_url:str
    short_code:str
    short_url:str
    clicks:int
    created_at:datetime
    expires_at:datetime|None


class UrlInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_url:HttpUrl
    short_code:str
    clicks:int
    is_active:bool
    created_at:datetime
    expires_at:datetime|None