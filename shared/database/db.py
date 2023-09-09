import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from shared.database.models import Base
from settings import settings


logger = logging.getLogger(__name__)


class DBService:
    def __init__(self) -> None:
        self.start_db()

    def get_url(self):
        url = URL.create(drivername='postgresql',
                         username=settings.POSTGRES_USER,
                         password=settings.POSTGRES_PASSWORD,
                         host=settings.POSTGRES_HOST,
                         port=settings.POSTGRES_PORT,
                         database=settings.POSTGRES_DB)
        return url

    def start_db(self):
        try:
            self.engine = create_engine(self.get_url())
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine,
                                        expire_on_commit=False)
            self.is_active = True
        except Exception:
            logger.error("Couln't start connection with database")
            self.is_active = False

    @contextmanager
    def get_session(self):
        if self.is_active and self.Session:
            try:
                with self.Session() as session:
                    yield session
            finally:
                session.close()
        else:
            raise ConnectionError('Database is not connected')


db = DBService()
