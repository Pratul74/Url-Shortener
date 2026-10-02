from db.database import Base
from models import Url
import datetime
from sqlalchemy import ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

class Analytics(Base):
    __tablename__ = "analytics"
    url_id : Mapped[int] = mapped_column(BigInteger, ForeignKey("urls.id", ondelete="CASCADE"), primary_key=True, unique=True, index=True, autoincrement=False)
    total_clicks : Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    country : Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict,)
    city : Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict,)
    browser : Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict,)
    device : Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict,)
    os : Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict,) 
    referrer : Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict,)
    updated_at : Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),nullable=False,)
    url : Mapped["Url"] = relationship(
        "Url",
        back_populates="analytics",
    )



