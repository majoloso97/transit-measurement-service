from pydantic import BaseModel


class VideoMetadata(BaseModel):
    width: int = None
    height: int = None
    fps: int = None
    total_frames: int = None
