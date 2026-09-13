from messaging.events import ClickEvent as ClickEventSchema
import asyncio
from .cache import AnalyticsCache
from .geoip import GeoIpService
from .ua_parser import UserAgentService
from repositories import AnalyticsRepository
from schemas import CreateAnalytics

class AnalyticsWorker:

    def __init__(self, geoip: GeoIpService, ua_parser: UserAgentService, analytics_repository: AnalyticsRepository, analytics_cache: AnalyticsCache):
        self.geoip = geoip
        self.ua_parser = ua_parser
        self.repo=analytics_repository
        self.cache=analytics_cache

    async def process_click(self, event: ClickEventSchema):
        geoip_info, ua_info = await asyncio.gather(
                self.geoip.lookup(event.ip),
                self.ua_parser.parse(event.user_agent),
        )

        analytics = CreateAnalytics(
            url_id=event.url_id,
            ip_address=event.ip,
            country=(geoip_info or {}).get('country') or "Unknown",
            city=(geoip_info or {}).get('city') or "Unknown",
            device=ua_info.get('device') or "Unknown",
            browser=ua_info.get('browser') or "Unknown",
            os=ua_info.get('os') or "Unknown",
            referrer=event.referrer or "",
            user_agent=event.user_agent,
        )

        await self.repo.create(analytics)
        await self.cache.update(analytics.url_id, analytics)
        
