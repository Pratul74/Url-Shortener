import uuid
from datetime import datetime
from db.database import Base
from sqlalchemy import Integer, Text, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, Mapped


class Url(Base):
    __tablename__ = 'urls'
    id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    original_url:Mapped[str] = mapped_column(Text, nullable=False)
    short_code:Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    clicks:Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active:Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    expires_at:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)