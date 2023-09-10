from shared.database.crud import CRUDManager
from shared.database.models import Video, Measurement, Detection
from shared.schemas.videos import VideoSchema, NewVideo, UpdateVideo
from shared.schemas.measurements import (MeasurementSchema,
                                         NewMeasurement,
                                         UpdateMeasurement,
                                         DetectionSchema)


class VideoManager:
    def __init__(self) -> None:
        self.crud_video = CRUDManager(db_model=Video,
                                      pydantic_create=NewVideo,
                                      pydantic_update=UpdateVideo,
                                      pydantic_response=VideoSchema)
        self.crud_measurement = CRUDManager(db_model=Measurement,
                                            pydantic_create=NewMeasurement,
                                            pydantic_update=UpdateMeasurement,
                                            pydantic_response=MeasurementSchema)
        self.crud_detection = CRUDManager(db_model=Detection,
                                          pydantic_create=DetectionSchema,
                                          pydantic_update=DetectionSchema,
                                          pydantic_response=DetectionSchema)

    def create_video(self, user_id: int, video: NewVideo) -> VideoSchema:
        video.owner_id = user_id
        with self.crud_video.db.get_session() as session:
            saved = self.crud_video.create_item(session=session,
                                                item_create=video)
        return saved
    
    def create_measurement(self, video_id: int,
                           measurement: NewMeasurement) -> MeasurementSchema:
        measurement.video_id = video_id
        counter_coordinates = [measurement.x1, measurement.y1,
                               measurement.x2, measurement.y2]
        if not all(counter_coordinates):
            measurement.x1 = 0.5
            measurement.y1 = 0.5
            measurement.x2 = 0.5
            measurement.y2 = 0.5
        with self.crud_measurement.db.get_session() as session:
            saved = self.crud_measurement.create_item(session=session,
                                                      item_create=measurement)
        return saved
    
    def create_detection(self, measurement_id: int,
                         detection: DetectionSchema) -> DetectionSchema:
        detection.measurement_id = measurement_id
        with self.crud_detection.db.get_session() as session:
            saved = self.crud_detection.create_item(session=session,
                                                    item_create=detection)
        return saved
    
    def user_update_video(self, video_id: int,
                          params: UpdateVideo) -> VideoSchema:
        with self.crud_video.db.get_session() as session:
            updated = self.crud_video.update_item(session=session,
                                                  item_id=video_id,
                                                  params=params)
        return updated
    
    def remove_video(self, video_id: int) -> VideoSchema:
        params = UpdateVideo(is_active=False)
        return self.user_update_video(video_id, params)
    
    def user_update_measurement(self, measurement_id: int,
                                params: UpdateMeasurement
                                ) -> MeasurementSchema:
        with self.crud_measurement.db.get_session() as session:
            updated = self.crud_measurement.update_item(session=session,
                                                        item_id=measurement_id,
                                                        params=params)
        return updated

    def remove_measurement(self, measurement_id: int) -> MeasurementSchema:
        params = UpdateMeasurement(is_active=False)
        return self.user_update_measurement(measurement_id, params)

    def get_video(self, video_id: int):
        with self.crud_video.db.get_session() as session:
            video = self.crud_video.get_item(session=session,
                                             item_id=video_id)
        return video

    def get_measurement(self, measurement_id: int):
        with self.crud_measurement.db.get_session() as session:
            measurement = self.crud_measurement.get_item(
                session=session,
                item_id=measurement_id)
        return measurement
