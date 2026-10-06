from messaging.events import ClickEvent as ClickEventSchema
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import asyncio
from .cache import AnalyticsCache
from .geoip import GeoIpService
from .ua_parser import UserAgentService
from repositories import AnalyticsRepository
from schemas import CreateAnalytics
from models import Analytics

class AnalyticsWorker:

    def __init__(self, geoip: GeoIpService, ua_parser: UserAgentService, session_factory: async_sessionmaker[AsyncSession], analytics_cache: AnalyticsCache):
        self.geoip = geoip
        self.ua_parser = ua_parser
        self.session_factory = session_factory
        self.cache=analytics_cache

    async def process_click(self, event: ClickEventSchema):
        geoip_info, ua_info = await asyncio.gather(
                self.geoip.lookup(event.ip),
                self.ua_parser.parse(event.user_agent),
        )

        analytics_schema = CreateAnalytics(
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

        await self.cache.update(event.url_id, analytics_schema)
        
