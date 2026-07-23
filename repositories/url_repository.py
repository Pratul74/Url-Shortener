from sqlalchemy.orm import Session

from models.url import Url
from repositories.base import BaseRepository


class URLRepository(BaseRepository[Url]):

    def __init__(self, db: Session):
        super().__init__(Url, db)

    def get_all(self):
        return self.db.query(Url).all()

    def get_by_short_code(self, short_code: str):
        return (
            self.db.query(Url)
            .filter(Url.short_code == short_code)
            .first()
        )

    def get_by_original_url(self, original_url: str):
        return (
            self.db.query(Url)
            .filter(Url.original_url == original_url)
            .first()
        )

    def short_code_exists(self, short_code: str) -> bool:
        return self.get_by_short_code(short_code) is not None

    def increment_clicks(self, url: Url):

        url.clicks += 1

        self.db.commit()

        self.db.refresh(url)

        return url

    def deactivate(self, url: Url):

        url.is_active = False

        self.db.commit()

        self.db.refresh(url)

        return url