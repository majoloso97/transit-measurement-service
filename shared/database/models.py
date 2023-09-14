from sqlalchemy import (Column, text, ForeignKey, Float,
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
    created_at = Column(DateTime(timezone=True),
                         server_default=text("(now() at time zone 'utc')"))
    name = Column(String(150))
    input_s3_key = Column(String(150))
    status = Column(String(15))
    is_active = Column(Boolean)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Integer)
    total_frames = Column(Integer)
    duration = Column(Integer)
    optimized_fps_ratio = Column(Float)
    optimized_s3_key = Column(String(150))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="videos")
    measurements = relationship("Measurement", back_populates="video")


class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    created_at = Column(DateTime(timezone=True),
                         server_default=text("(now() at time zone 'utc')"))
    name = Column(String(150))
    status = Column(String(15))
    is_active = Column(Boolean)
    x1 = Column(Float)
    y1 = Column(Float)
    x2 = Column(Float)
    y2 = Column(Float)
    output_s3_key = Column(String(150))
    detections_count = Column(Integer)
    global_frequency = Column(Float)

    video = relationship("Video", back_populates="measurements")
    detections = relationship("Detection", back_populates="measurement")


class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id = Column(Integer, ForeignKey("measurements.id"))
    class_name = Column(String(30))
    count = Column(Integer)
    frequency = Column(Float)

    measurement = relationship("Measurement", back_populates="detections")
