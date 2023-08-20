from sqlalchemy import (Column, text,
                        String, DateTime, Integer)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"
    id = Column(UUID,
                server_default=text("gen_random_uuid()"),
                primary_key=True)
    uploaded_at = Column(DateTime(timezone=True),
                         server_default=text("(now() at time zone 'utc')"))
    name = Column(String(150))
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Integer)
    total_frames = Column(Integer)
