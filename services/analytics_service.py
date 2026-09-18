import asyncio
import uuid
from datetime import date
from repositories import AnalyticsRepository
from .base import BaseService


class AnalyticsService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.repo = AnalyticsRepository(db)

    async def get_analytics_dashboard(
        self,
        url_id: uuid.UUID,
        start_date: date,
        end_date: date,
        target_date: date,
        month: int,
        year: int,
        limit: int = 3,
    ):
        (
            total_clicks,
            clicks_per_year,
            clicks_per_months,
            clicks_per_day,
            top_country,
            top_city,
            top_device,
            top_browser,
            top_os,
            top_ip,
            top_n_country,
            top_n_cities,
            top_n_os,
            top_n_ips,
            top_n_browsers,
            click_per_country,
            click_per_city,
            click_per_os,
            click_per_browser,
            click_between_dates,
            clicks_in_year,
            clicks_in_month,
            clicks_in_day,
        ) = await asyncio.gather(
            self.repo.get_total_clicks(url_id=url_id),
            self.repo.get_clicks_per_year(url_id=url_id),
            self.repo.get_clicks_per_month(url_id=url_id, year=year),
            self.repo.get_clicks_per_day(url_id=url_id, start_date=start_date, end_date=end_date),
            self.repo.get_top_country(url_id=url_id),
            self.repo.get_top_city(url_id=url_id),
            self.repo.get_top_device(url_id=url_id),
            self.repo.get_top_browser(url_id=url_id),
            self.repo.get_top_os(url_id=url_id),
            self.repo.get_top_ip(url_id=url_id),
            self.repo.get_top_n_countries(url_id=url_id, limit=limit),
            self.repo.get_top_n_cities(url_id=url_id, limit=limit),
            self.repo.get_top_n_os(url_id=url_id, limit=limit),
            self.repo.get_top_n_ips(url_id=url_id, limit=limit),
            self.repo.get_top_n_browsers(url_id=url_id, limit=limit),
            self.repo.click_per_country(url_id=url_id),
            self.repo.click_per_city(url_id=url_id),
            self.repo.click_per_os(url_id=url_id),
            self.repo.click_per_browser(url_id=url_id),
            self.repo.get_clicks_between_dates(url_id=url_id, start_date=start_date, end_date=end_date),
            self.repo.get_clicks_in_year(url_id=url_id, year=year),
            self.repo.get_clicks_in_month(url_id=url_id, month=month, year=year),
            self.repo.get_clicks_on_date(url_id=url_id, target_date=target_date),
        )

        return {
            "total_clicks": total_clicks,
            "clicks_per_year": clicks_per_year,
            "clicks_per_months": clicks_per_months,
            "clicks_per_day": clicks_per_day,
            "top_country": top_country,
            "top_city": top_city,
            "top_device": top_device,
            "top_browsers": top_browser,
            "top_os": top_os,
            "top_ip": top_ip,
            "top_n_country": top_n_country,
            "top_n_cities": top_n_cities,
            "top_n_os": top_n_os,
            "top_n_ips": top_n_ips,
            "top_n_browsers": top_n_browsers,
            "click_per_country": click_per_country,
            "click_per_city": click_per_city,
            "click_per_os": click_per_os,
            "click_per_browser": click_per_browser,
            "click_between_dates": click_between_dates,
            "clicks_in_year": clicks_in_year,
            "clicks_in_month": clicks_in_month,
            "clicks_in_day": clicks_in_day,
        }