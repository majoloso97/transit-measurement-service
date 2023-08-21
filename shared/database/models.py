from sqlalchemy import (Column, text, ForeignKey,
                        String, DateTime, Integer, Boolean)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    password = Column(String(100))
    email = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    description = Column(String(100))
    photo = Column(String(100))
    created_at = Column(DateTime(timezone=True),
                         server_default=text("(now() at time zone 'utc')"))
    last_active = Column(DateTime(timezone=True),
                         server_default=text("(now() at time zone 'utc')"))
    is_active = Column(Boolean)

    videos = relationship("Video", back_populates="owner")


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uploaded_at = Column(DateTime(timezone=True),
                         server_default=text("(now() at time zone 'utc')"))
    name = Column(String(150))
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Integer)
    total_frames = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="videos")
