from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from shared.database.models import Base
from settings import settings


class DbService:
    def __init__(self) -> None:
        try:
            self.engine = create_engine(self.get_url())
            Base.metadata.create_all(self.engine)
            self.session = sessionmaker(self.engine)
            self.is_active = True
        except Exception:
            self.is_active = False

    def get_url(self):
        url = URL.create(drivername='postgresql',
                         username=settings.POSTGRES_USER,
                         password=settings.POSTGRES_PASSWORD,
                         host=settings.POSTGRES_HOST,
                         port=settings.POSTGRES_PORT,
                         database=settings.POSTGRES_DB)
        return url

    def save(self, record):
        if not self.is_active:
            raise ConnectionError('DB not connected')
        with self.session.begin() as session:
            session.add(record)
            session.commit()


db = DbService()
