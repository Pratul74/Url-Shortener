from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from core.config import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True
)

Base = declarative_base()