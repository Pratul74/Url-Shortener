import uuid
from db.database import Base
from sqlalchemy import ForeignKey, String, DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
class ClickEvent(Base):
    __tablename__ = "click_events"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    url_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("urls.id"), nullable=False, index=True)
    clicked_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    ip_address : Mapped[str] = mapped_column(String(45), nullable=False)
    country : Mapped[str] = mapped_column(String(100))
    city : Mapped[str] = mapped_column(String(100))
    device : Mapped[str] = mapped_column(String(100))
    browser : Mapped[str] = mapped_column(String(100))
    os : Mapped[str] = mapped_column(String(100))
    referrer : Mapped[str] = mapped_column(Text)
    user_agent : Mapped[str] = mapped_column(Text)

    url = relationship(
        "Url",
        back_populates="click_events",
    )
