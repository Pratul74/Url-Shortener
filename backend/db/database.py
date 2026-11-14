from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from backend.core import get_database_setting

def get_async_database_url(url: str) -> str:
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            url = "postgresql+asyncpg://" + url[len(prefix):]
            break

    parsed = make_url(url)
    if parsed.drivername == "postgresql+asyncpg" and "sslmode" in parsed.query:
        query = dict(parsed.query)
        query.setdefault("ssl", query.pop("sslmode"))
        parsed = parsed.set(query=query)
    return parsed.render_as_string(hide_password=False)

settings = get_database_setting()

engine = create_async_engine(
    url=get_async_database_url(settings.DATABASE_URL),
    pool_pre_ping=True,
)

Base = declarative_base()
