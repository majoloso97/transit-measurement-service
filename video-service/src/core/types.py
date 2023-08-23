from pydantic import BaseModel, ConfigDict
import numpy as np


class VideoMetadata(BaseModel):
    width: int = None
    height: int = None
    fps: int = None
    total_frames: int = None


class FrameDetection(BaseModel):
    xyxy: type[np.ndarray]
    confidence: type[np.ndarray]
    class_id: type[np.ndarray]
    class_label: type[np.ndarray]

    model_config = ConfigDict(arbitrary_types_allowed = True)
