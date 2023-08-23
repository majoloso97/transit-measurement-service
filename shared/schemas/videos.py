from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, ConfigDict
import numpy as np


class BaseVideo(BaseModel):
    id: int = None
    owner_id: int = None
    is_active: bool = True


class VideoSchema(BaseVideo):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    name: str
    path: str = None
    uploaded_at: datetime
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    total_frames: Optional[int] = None
    duration: Optional[int] = None


class NewVideo(BaseVideo):
    name: str = str(uuid4())
    path: str = None
    uploaded_at: datetime = datetime.now(tz=timezone.utc)
    status: str = 'Created'


class UpdateVideoAPI(BaseVideo):
    name: str = None
    is_active: bool = None


class UpdateVideoMetadata(BaseVideo):
    width: int = None
    height: int = None
    fps: int = None
    total_frames: int = None
    duration: int = None
    status: str = 'In Progress'


class FrameDetection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed = True)
    
    xyxy: type[np.ndarray]
    confidence: type[np.ndarray]
    class_id: type[np.ndarray]
    class_label: type[np.ndarray]
