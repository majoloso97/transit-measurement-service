from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, ConfigDict


class DetectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    measurement_id: Optional[int]
    class_name: Optional[str]
    count: Optional[int]
    frequency: Optional[float]


class BaseMeasurement(BaseModel):
    id: int = None
    video_id: int = None


class MeasurementSchema(BaseMeasurement):
    model_config = ConfigDict(from_attributes=True)

    id: int
    video_id: int
    created_at: datetime
    name: str
    status: str
    x1: float = None
    y1: float = None
    x2: float = None
    y2: float = None
    output_s3_key: Optional[str] = None
    detections_count: Optional[int] = None
    global_frequency: Optional[float] = None
    detections: list[DetectionSchema] | None = None


class UpdateMeasurement(BaseMeasurement):
    name: str = None
    is_active: bool = None


class NewMeasurement(BaseMeasurement):
    video_id: int = None
    name: str = str(uuid4())
    x1: float = None
    y1: float = None
    x2: float = None
    y2: float = None
    status: str = 'Created'
