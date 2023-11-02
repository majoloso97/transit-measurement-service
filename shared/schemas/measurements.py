from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, ConfigDict


class DetectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = None
    measurement_id: int = None
    class_name: Optional[str]
    count: Optional[int]
    frequency: Optional[float]


class BaseMeasurement(BaseModel):
    id: int = None
    video_id: int = None
    is_active: bool = True


class MeasurementSchema(BaseMeasurement):
    model_config = ConfigDict(from_attributes=True)

    id: int
    video_id: int
    created_at: datetime
    name: str
    status: str
    is_active: bool
    x1: Optional[float] = None
    y1: Optional[float] = None
    x2: Optional[float] = None
    y2: Optional[float] = None
    upload_url: Optional[str] = None
    output_s3_key: Optional[str] = None
    output_video_url: Optional[str] = None
    detections_count: Optional[int] = None
    global_frequency: Optional[float] = None
    detections: list[DetectionSchema] | None = None


class NewMeasurement(BaseMeasurement):
    video_id: int = None
    name: str = str(uuid4())
    output_s3_key: str = None
    x1: float = -1.0
    y1: float = -1.0
    x2: float = -1.0
    y2: float = -1.0
    status: str = 'REQUESTED'


class UpdateMeasurementAPI(BaseMeasurement):
    name: str = None
    is_active: bool = None
    status: str = None


class UpdateMeasurementInternal(BaseMeasurement):
    status: str = None
    output_s3_key: str = None
    output_video_url: str = None
    detections_count: int = None
    global_frequency: float = None
