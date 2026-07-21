from fastapi import HTTPException, status
from datetime import datetime, timezone
from utils.generator import generate_code
from repositories.url_repository import URLRepository
from models.url import Url

class UrlShortenerService:

    def __init__(self, db):
        self.repo=URLRepository(db)
        
    def generate_short_code(self):
        while True:
            short_code = generate_code()

            if not self.repo.short_code_exists(short_code):
                return short_code
            
    def create_short_url(self, original_url, custom_alias=None, expires_at=None):
        if custom_alias:
            if self.repo.short_code_exists(custom_alias):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Alias already exists.')
            short_code=custom_alias

        else:
            short_code=self.generate_short_code()
        return self.repo.create(
            original_url=original_url, 
            custom_alias=custom_alias, 
            expires_at=expires_at
            )
    
    def get_original_url(self, short_code:str):
        url = self.repo.get_by_short_code(short_code)

        if not url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Url not found.")
        
        if not url.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Url is not active.")
        
        if url.expires_at and url.expires_at<datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Url has expired.")
        
        self.repo.increment_clicks(url)

        return url

