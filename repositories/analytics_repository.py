import uuid
from datetime import date
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from models import ClickEvent as ClickEventModel
from schemas import Country, City, Browser, Os, Device, Ip, CreateAnalytics


class AnalyticsRepository(BaseRepository[ClickEventModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(ClickEventModel, db)

    async def create(self, analytics: CreateAnalytics):
        click_event = self.model(**analytics.model_dump())
        self.db.add(click_event)
        await self.db.commit()
        await self.db.refresh(click_event)
        return click_event

    # Total Clicks of a shorten url
    async def get_total_clicks(self, url_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id)).where(self.model.url_id == url_id)
        )
        return result.scalar() or 0

    async def _top_by(self, url_id: uuid.UUID, schema, column, limit=None):
        stmt = (
            select(column, func.count(self.model.id).label('click_count'))
            .where(self.model.url_id == url_id)
            .group_by(column)
            .order_by(func.count(self.model.id).desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        results = result.all()
        if not results:
            return []
        field_name = column.key
        return [
            schema(**{field_name: value, 'click_count': click_count})
            for value, click_count in results
            ]
    async def _top_one_by(self, url_id: uuid.UUID, schema, column):
        results= await self._top_by(
            url_id=url_id,
            schema=schema,
            column=column,
            limit=1
        )
        return results[0] if results else None

    # Country with most clicks
    async def get_top_country(self, url_id: uuid.UUID) -> Country:
        return await self._top_one_by(url_id=url_id, schema=Country, column=self.model.country)

    # City with most clicks
    async def get_top_city(self, url_id: uuid.UUID) -> City:
        return await self._top_one_by(url_id=url_id, schema=City, column=self.model.city)

    # Browser with most clicks
    async def get_top_browser(self, url_id: uuid.UUID) -> Browser:
        return await self._top_one_by(url_id=url_id, schema=Browser, column=self.model.browser)

    # Device with most clicks
    async def get_top_device(self, url_id: uuid.UUID) -> Device:
        return await self._top_one_by(url_id=url_id, schema=Device, column=self.model.device)

    # Os with most clicks
    async def get_top_os(self, url_id: uuid.UUID) -> Os:
        return await self._top_one_by(url_id=url_id, schema=Os, column=self.model.os)

    # Clicks as per countries
    async def click_per_country(self, url_id: uuid.UUID):
        return await self._top_by(url_id=url_id, schema=Country, column=self.model.country)

    # Clicks as per city
    async def click_per_city(self, url_id: uuid.UUID):
        return await self._top_by(url_id=url_id, schema=City, column=self.model.city)
        

    # Clicks as per Browser
    async def click_per_browser(self, url_id: uuid.UUID):
        return await self._top_by(url_id=url_id, schema=Browser, column=self.model.browser)

    # Clicks as per os
    async def click_per_os(self, url_id: uuid.UUID):
        return await self._top_by(url_id=url_id, schema=Os, column=self.model.os)

    # ip with most clicks
    async def get_top_ip(self, url_id: uuid.UUID) -> Ip:
        return await self._top_one_by(url_id=url_id, schema=Ip, column=self.model.ip_address)

    
    #N ips with most clicks
    async def get_top_n_ips(self, url_id: uuid.UUID, limit: int = 3):
        return await self._top_by(url_id=url_id, schema=Ip, column=self.model.ip_address, limit=limit)

    #N countries with most clicks
    async def get_top_n_countries(self, url_id: uuid.UUID, limit: int = 3):
        return await self._top_by(url_id=url_id, schema=Country, column=self.model.country, limit=limit)

    #N cities with most clicks
    async def get_top_n_cities(self, url_id: uuid.UUID, limit: int = 3):
        return await self._top_by(url_id=url_id, schema=City, column=self.model.city, limit=limit)

    #N browsers with most clicks
    async def get_top_n_browsers(self, url_id: uuid.UUID, limit: int = 3):
        return await self._top_by(url_id=url_id, schema=Browser, column=self.model.browser, limit=limit)

    #N OSs with most clicks
    async def get_top_n_os(self, url_id: uuid.UUID, limit: int = 3):
        return await self._top_by(url_id=url_id, schema=Os, column=self.model.os, limit=limit)


    # Total clicks between two dates (inclusive), e.g. start=2024-01-01, end=2024-01-31
    async def get_clicks_between_dates(self, url_id: uuid.UUID, start_date: date, end_date: date) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id))
            .where(
                self.model.url_id == url_id,
                func.date(self.model.clicked_at) >= start_date,
                func.date(self.model.clicked_at) <= end_date,
            )
        )
        return result.scalar() or 0

    # Clicks on one specific date, e.g. target_date=2024-01-15
    async def get_clicks_on_date(self, url_id: uuid.UUID, target_date: date) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id))
            .where(
                self.model.url_id == url_id,
                func.date(self.model.clicked_at) == target_date,
            )
        )
        return result.scalar() or 0

    # Clicks in a specific month of a specific year, e.g. month=1, year=2024
    async def get_clicks_in_month(self, url_id: uuid.UUID, month: int, year: int) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id))
            .where(
                self.model.url_id == url_id,
                extract('month', self.model.clicked_at) == month,
                extract('year', self.model.clicked_at) == year,
            )
        )
        return result.scalar() or 0

    # Clicks in a specific year, e.g. year=2024
    async def get_clicks_in_year(self, url_id: uuid.UUID, year: int) -> int:
        result = await self.db.execute(
            select(func.count(self.model.id))
            .where(
                self.model.url_id == url_id,
                extract('year', self.model.clicked_at) == year,
            )
        )
        return result.scalar() or 0

    # Daily click breakdown between two dates (for time-series charts)
    async def get_clicks_per_day(self, url_id: uuid.UUID, start_date: date, end_date: date):
        result = await self.db.execute(
            select(
                func.date(self.model.clicked_at).label('day'),
                func.count(self.model.id).label('click_count'),
            )
            .where(
                self.model.url_id == url_id,
                func.date(self.model.clicked_at) >= start_date,
                func.date(self.model.clicked_at) <= end_date,
            )
            .group_by(func.date(self.model.clicked_at))
            .order_by(func.date(self.model.clicked_at))
        )
        results = result.all()
        return [{"date": row.day, "click_count": row.click_count} for row in results]

    # Monthly click breakdown for a given year
    async def get_clicks_per_month(self, url_id: uuid.UUID, year: int):
        result = await self.db.execute(
            select(
                extract('month', self.model.clicked_at).label('month'),
                func.count(self.model.id).label('click_count'),
            )
            .where(
                self.model.url_id == url_id,
                extract('year', self.model.clicked_at) == year,
            )
            .group_by(extract('month', self.model.clicked_at))
            .order_by(extract('month', self.model.clicked_at))
        )
        results = result.all()
        return [{"month": int(row.month), "click_count": row.click_count} for row in results]

    # Yearly click breakdown (all-time)
    async def get_clicks_per_year(self, url_id: uuid.UUID):
        result = await self.db.execute(
            select(
                extract('year', self.model.clicked_at).label('year'),
                func.count(self.model.id).label('click_count'),
            )
            .where(self.model.url_id == url_id)
            .group_by(extract('year', self.model.clicked_at))
            .order_by(extract('year', self.model.clicked_at))
        )
        results = result.all()
        return [{"year": int(row.year), "click_count": row.click_count} for row in results]



