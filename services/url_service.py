from datetime import datetime, timezone, timedelta

from core import settings
from exceptions import AliasAlreadyExistsException, UrlNotFoundException, UrlInactiveException, UrlExpiredException
from mappers import UrlMapper
from repositories.url_repository import URLRepository
from utils.generator import generate_code
from .base import BaseService

class UrlShortenerService(BaseService):

    def __init__(self, db):
        super().__init__(db)
        self.repo=URLRepository(db)

    @staticmethod
    def _is_expired(expires_at: datetime | None) -> bool:
        if expires_at is None:
            return False

        now = datetime.now(timezone.utc)

        if expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)

        return expires_at < now
        
    def generate_short_code(self):
        while True:
            short_code = generate_code()

            if not self.repo.short_code_exists(short_code):
                return short_code
            
    def create_short_url(self, original_url, custom_alias=None, expires_at=None, user_id=None):
        if custom_alias:
            if self.repo.short_code_exists(custom_alias):
                raise AliasAlreadyExistsException()
            short_code=custom_alias
        else:
            short_code=self.generate_short_code()
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        return self.repo.create(
            original_url=original_url, 
            short_code=short_code, 
            expires_at=expires_at,
            user_id=user_id
            )
    
    #This will use redis cache
    def get_original_url(self, short_code:str):
        url = self.repo.get_by_short_code(short_code)

        if not url:
            raise UrlNotFoundException()
        
        if not url.is_active:
            raise UrlInactiveException()
        
        if self._is_expired(url.expires_at):
            raise UrlExpiredException()
        
        self.repo.increment_clicks(url)

        return url
    
    def url_details(self, user_id, short_code):
        url = self.repo.get_by_short_code(short_code)
        if not url:
            raise UrlNotFoundException()

        if url.user_id != user_id:
            raise UrlNotFoundException()
        
        if not url.is_active:
            raise UrlInactiveException()
        
        if self._is_expired(url.expires_at):
            raise UrlExpiredException()
        
        return UrlMapper.to_details(url, settings.BASE_URL)

    
    def delete_url(self, user_id:int, short_code):
        url = self.repo.get_by_short_code(short_code)

        if not url:
            raise UrlNotFoundException()

        if url.user_id != user_id:
            raise UrlNotFoundException()
        
        self.repo.deactivate(user_id, url)

    def list_url_by_user(self, user_id):
        urls = self.repo.get_all_by_user(user_id)

        return [UrlMapper.to_details(url, settings.BASE_URL) for url in urls]
