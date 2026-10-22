import asyncio
import logging
import time
from pathlib import Path
from threading import Lock

from geoip2.database import Reader
from geoip2.errors import AddressNotFoundError

from backend.core import get_geoip_setting

logger = logging.getLogger(__name__)

RELOAD_CHECK_INTERVAL = 60 


class GeoIpService:
    def __init__(self, settings=None):
        self.settings = settings or get_geoip_setting()
        self.db_path = Path(self.settings.GEOLITE2_PATH)
        self.reader: Reader | None = None
        self.db_signature: tuple[int, int] | None = None
        self._last_check = 0.0
        self._lock = Lock()

    def _get_reader(self) -> Reader:
        now = time.monotonic()
        if self.reader is not None and now - self._last_check < RELOAD_CHECK_INTERVAL:
            return self.reader
        self._last_check = now

        try:
            stat = self.db_path.stat()
        except FileNotFoundError:
            if self.reader is not None:
                logger.warning("GeoLite2 DB missing, using existing reader")
                return self.reader
            raise

        signature = (stat.st_mtime_ns, stat.st_size)
        if self.reader is None or signature != self.db_signature:
            new_reader = Reader(str(self.db_path))
            old_reader, self.reader = self.reader, new_reader
            self.db_signature = signature
            if old_reader is not None:
                old_reader.close()
            logger.info("GeoLite2 database loaded/refreshed")
        return self.reader

    def _lookup_sync(self, ip_address: str) -> dict | None:
        print(ip_address)
        with self._lock:
            reader = self._get_reader()
            try:
                response = reader.city(ip_address)
            except AddressNotFoundError:
                logger.debug("No GeoIP record for %s", ip_address)
                return None

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
            return await asyncio.to_thread(self._lookup_sync, ip_address)
        except ValueError:
            logger.warning("Invalid IP address: %s", ip_address)
            return None
        except Exception:
            logger.exception("GeoIP lookup failed for %s", ip_address)
            return None

    def _close_sync(self):
        with self._lock:
            if self.reader is not None:
                self.reader.close()
                self.reader = None
                self.db_signature = None

    async def close(self):
        await asyncio.to_thread(self._close_sync)