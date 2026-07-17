from fastapi import HTTPException, status
from utils.generator import generate_code
from models.url import Url

class UrlShortenerService:

    def __init__(self, db):
        self.db=db

    def short_code_exists(self, short_code):
        return (
            self.db.query(Url).filter(Url.short_code == short_code).first() is not None
        )
        
    def generate_short_code(self):
        while True:
            short_code = generate_code()

            if not self.short_code_exists(short_code):
                return short_code
            
    def create_short_url(self, orginal_url, custom_alias=None, expires_at=None):
        if custom_alias:
            if self.short_code_exists(custom_alias):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Alias already exists.')
            short_code=custom_alias

        else:
            short_code=self.generate_short_code()
        url = Url(orginal_url=orginal_url, short_code=short_code, expires_at=expires_at)
        self.db.add(url)
        self.db.commit()
        self.db.refresh(url)
