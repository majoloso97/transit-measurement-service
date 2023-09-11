import requests
from uuid import uuid4
from settings import settings
from shared.database.crud import CRUDManager
from shared.database.models import Video, Measurement, Detection
from shared.schemas.videos import (VideoSchema,
                                   NewVideo,
                                   UpdateVideoAPI,
                                   UpdateVideoInternal)
from shared.schemas.measurements import (MeasurementSchema,
                                         NewMeasurement,
                                         UpdateMeasurementAPI,
                                         UpdateMeasurementInternal,
                                         DetectionSchema)
from shared.aws.factory import AWSServiceFactory


class VideoManager:
    def __init__(self, usage: str = 'external') -> None:
        s3_config = {'bucket_name': settings.AWS_BUCKET_NAME}
        self.s3 = AWSServiceFactory.get_service(service='s3',
                                                config=s3_config)
        update_classes = {
            'video': {
                'internal': UpdateVideoInternal,
                'external': UpdateVideoAPI
            },
            'measurement': {
                'internal': UpdateMeasurementInternal,
                'external': UpdateMeasurementAPI
            }
        }
        video_cls = update_classes['video'][usage]
        measurement_cls = update_classes['measurement'][usage]
        self.crud_video = CRUDManager(db_model=Video,
                                    pydantic_create=NewVideo,
                                    pydantic_update=video_cls,
                                    pydantic_response=VideoSchema)
        self.crud_measurement = CRUDManager(db_model=Measurement,
                                            pydantic_create=NewMeasurement,
                                            pydantic_update=measurement_cls,
                                            pydantic_response=MeasurementSchema)
        self.crud_detection = CRUDManager(db_model=Detection,
                                        pydantic_create=DetectionSchema,
                                        pydantic_update=DetectionSchema,
                                        pydantic_response=DetectionSchema)

    def create_video(self, user_id: int, video: NewVideo) -> VideoSchema:
        video.owner_id = user_id
        video.input_s3_key = self.generate_video_key('input')
        with self.crud_video.db.get_session() as session:
            saved = self.crud_video.create_item(session=session,
                                                item_create=video)
        if saved.status.upper() == 'CREATED':
            url = self.s3.generate_presigned_url(operation='put',
                                                 key=saved.input_s3_key)
            saved.upload_url = url

        saved = self.inject_urls(saved)
        return saved
    
    def create_measurement(self, video_id: int,
                           measurement: NewMeasurement) -> MeasurementSchema:
        measurement.video_id = video_id
        measurement.output_s3_key = self.generate_video_key('predictions')
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
    
    def update_video(self, video_id: int,
                     params: UpdateVideoAPI | UpdateVideoInternal,
                     add_upload_url: bool = False,
                     key_from: str = None
                     ) -> VideoSchema:
        with self.crud_video.db.get_session() as session:
            updated = self.crud_video.update_item(session=session,
                                                  item_id=video_id,
                                                  item_update=params)
        if add_upload_url:
            key = getattr(updated, key_from, None)
            url = self.s3.generate_presigned_url(operation='put',
                                                 key=key)
            updated.upload_url = url
        updated = self.inject_urls(updated)
        return updated
    
    def remove_video(self, video_id: int) -> VideoSchema:
        params = UpdateVideoAPI(is_active=False)
        return self.update_video(video_id, params)
    
    def update_measurement(self, measurement_id: int,
                           params: UpdateMeasurementAPI | UpdateMeasurementInternal,
                           add_upload_url: bool = False,
                           key_from: str = None
                           ) -> MeasurementSchema:
        with self.crud_measurement.db.get_session() as session:
            updated = self.crud_measurement.update_item(session=session,
                                                        item_id=measurement_id,
                                                        item_update=params)
        if add_upload_url:
            key = getattr(updated, key_from, None)
            url = self.s3.generate_presigned_url(operation='put',
                                                 key=key)
            updated.upload_url = url
        updated = self.inject_urls(updated)
        return updated

    def remove_measurement(self, measurement_id: int) -> MeasurementSchema:
        params = UpdateMeasurementAPI(is_active=False)
        return self.update_measurement(measurement_id, params)

    def get_video(self, video_id: int):
        with self.crud_video.db.get_session() as session:
            video = self.crud_video.get_item(session=session,
                                             item_id=video_id)
        video = self.inject_urls(video)
        return video

    def get_measurement(self, measurement_id: int):
        with self.crud_measurement.db.get_session() as session:
            measurement = self.crud_measurement.get_item(
                session=session,
                item_id=measurement_id)
        measurement = self.inject_urls(measurement)
        return measurement

    def generate_video_key(self, stage: str):
        id = str(uuid4())
        key = f'videos/{stage}/{id}.mp4'
        return key
    
    def inject_urls(self, instance):
        if getattr(instance, 'input_s3_key', None):
            url = self.s3.generate_presigned_url(operation='get',
                                                 key=instance.input_s3_key)
            instance.input_video_url = url

        if getattr(instance, 'optimized_s3_key', None):
            url = self.s3.generate_presigned_url(operation='get',
                                                 key=instance.optimized_s3_key)
            instance.optimized_video_url = url

        if getattr(instance, 'output_s3_key', None):
            url = self.s3.generate_presigned_url(operation='get',
                                                 key=instance.output_s3_key)
            instance.output_video_url = url

        return instance
