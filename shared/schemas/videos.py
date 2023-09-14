from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, ConfigDict
import numpy as np
from .measurements import MeasurementSchema


class BaseVideo(BaseModel):
    id: int = None
    owner_id: int = None
    is_active: bool = True


class VideoSchema(BaseVideo):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    name: str
    status: Optional[str] = None
    input_s3_key: str = None
    upload_url: Optional[str] = None
    input_video_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    total_frames: Optional[int] = None
    duration: Optional[int] = None
    optimized_fps_ratio: Optional[float] = None
    optimized_s3_key: Optional[str] = None
    optimized_video_url: Optional[str] = None
    measurements: list[MeasurementSchema] | None = None


class NewVideo(BaseVideo):
    name: str = str(uuid4())
    input_s3_key: str = None
    created_at: datetime = datetime.now(tz=timezone.utc)
    status: str = 'CREATED'


class UpdateVideoAPI(BaseVideo):
    name: str = None
    is_active: bool = None
    status: str = None


class UpdateVideoInternal(BaseVideo):
    status: str = None
    width: int = None
    height: int = None
    fps: int = None
    total_frames: int = None
    duration: int = None
    optimized_fps_ratio: float = None
    optimized_s3_key: str = None


class FrameDetection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)
    
    xyxy: type[np.ndarray]
    confidence: type[np.ndarray]
    class_id: type[np.ndarray]
    class_label: type[np.ndarray]
