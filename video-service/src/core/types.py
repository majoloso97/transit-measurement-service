from pydantic import BaseModel
import numpy as np


class VideoMetadata(BaseModel):
    width: int = None
    height: int = None
    fps: int = None
    total_frames: int = None


class FrameDetection(BaseModel):
    xyxy: np.array
    confidence: np.array
    class_id: np.array
    class_label: np.array

    class Config:
        arbitrary_types_allowed = True
