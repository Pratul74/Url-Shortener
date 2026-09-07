from geoip2.database import Reader
from core import settings

class GeoIpService:
    def __init__(self):
        self.reader = Reader(settings.GeoLite2_PATH)

    def lookup(self, ip_address) -> dict | None:
        try:
            response=self.reader.city(ip_address)

            return {
                "country": response.country.name,
                "country_code": response.country.iso_code,
                "continent": response.continent.name,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude
            }
        except Exception as e:
            return None

    def close(self):
        self.reader.close()