from geoip2.database import Reader
from pathlib import Path
from core import settings
from threading import RLock
import logging
import asyncio

logger = logging.getLogger(__name__)

class GeoIpService:
    def __init__(self):
        self.db_path=Path(settings.GEOLITE2_PATH)
        self.reader: Reader | None = None
        self.db_signature: tuple[int, int] | None = None
        self._lock=RLock()

    def _get_reader(self) -> Reader:
        stat = self.db_path.stat()
        signature = (stat.st_mtime_ns, stat.st_size)
        if self.reader is None or signature != self.db_signature:
            new_reader = Reader(str(self.db_path))
            old_reader = self.reader
            self.reader = new_reader
            self.db_signature=signature
            if old_reader is not None:
                old_reader.close()
            logger.info("GeoLite2 database updated and refreshed")
        return self.reader

    def _lookup_sync(self, ip_address: str) -> dict | None:
        with self._lock:
            reader = self._get_reader()
            response = reader.city(ip_address)

            return {
                "country": response.country.name,
                "country_code": response.country.iso_code,
                "continent": response.continent.name,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
            }

    async def lookup(self, ip_address: str) -> dict | None:
        try:
            return await asyncio.to_thread(
                self._lookup_sync,
                ip_address,
            )
        except Exception:
            logger.exception(
                "GeoIP lookup failed for %s",
                ip_address,
            )
            return None

    def _close_sync(self):
        with self._lock:
            if self.reader is not None:
                self.reader.close()
                self.reader = None
                self.db_signature = None

    async def close(self):
        await asyncio.to_thread(self._close_sync)
