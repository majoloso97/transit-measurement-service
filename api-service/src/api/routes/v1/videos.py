from fastapi import APIRouter, Depends
from api.dependencies.auth import get_current_active_user
from api.errors import raise_http_exception
from shared.queue.queue import q
from shared.schemas.videos import VideoSchema, NewVideo, UpdateVideoAPI
from shared.schemas.measurements import (MeasurementSchema,
                                         NewMeasurement,
                                         UpdateMeasurementAPI)
from shared.schemas.users import UserSchema
from shared.service.videos import VideoManager


router = APIRouter(prefix='/api/v1/videos')
video_manager = VideoManager()


@router.post('/', response_model=VideoSchema)
def create_video(video: NewVideo,
                 current_user: UserSchema =
                 Depends(get_current_active_user)) -> VideoSchema:
    return video_manager.create_video(user_id=current_user.id,
                                      video=video)


@router.get('/', response_model=list[VideoSchema])
def get_videos(current_user: UserSchema =
               Depends(get_current_active_user)) -> list[VideoSchema]:
    videos = video_manager.get_videos()
    user_videos = filter(lambda x: x.owner_id == current_user.id, videos)
    return list(user_videos)


@router.get('/{id}/', response_model=VideoSchema)
def get_video(id: int,
             current_user: UserSchema =
             Depends(get_current_active_user)) -> VideoSchema:
    return video_manager.get_video(video_id=id)


@router.patch('/{id}/', response_model=VideoSchema)
def modify_video(id: int,
                params: UpdateVideoAPI,
                current_user: UserSchema =
                Depends(get_current_active_user)) -> VideoSchema:
    return video_manager.update_video(video_id=id,
                                      params=params)


@router.patch('/{id}/confirm-upload/', response_model=VideoSchema)
def modify_video(id: int,
                 current_user: UserSchema =
                Depends(get_current_active_user)) -> VideoSchema:
    params = UpdateVideoAPI(status='QUEUED')
    q.lpush('VIDEO_TODO', id)
    return video_manager.update_video(video_id=id,
                                      params=params)


@router.delete('/{id}/', response_model=VideoSchema)
def deactivate_video(id: int,
                     current_user: UserSchema =
                     Depends(get_current_active_user)) -> VideoSchema:
    return video_manager.remove_video(video_id=id)


@router.post('/{video_id}/measurements/',
             response_model=MeasurementSchema)
def create_measurement(video_id: int,
                       measurement: NewMeasurement,
                       current_user: UserSchema =
                       Depends(get_current_active_user)) -> MeasurementSchema:
    video = video_manager.get_video(video_id)
    requires_queuing = video.status == 'OPTIMIZED'
    if requires_queuing:
        measurement.status = 'QUEUED'
    
    measurement = video_manager.create_measurement(video_id=video_id,
                                                   measurement=measurement)
    if requires_queuing: q.lpush('MEASUREMENTS_TODO', measurement.id)
    return measurement


@router.get('/{video_id}/measurements/{id}/',
            response_model=MeasurementSchema)
def get_video(video_id: int,
              id: int,
              current_user: UserSchema =
              Depends(get_current_active_user)) -> MeasurementSchema:
    measurement = video_manager.get_measurement(measurement_id=id)
    if measurement.video_id == video_id:
        return measurement
    raise_http_exception(404, f'Measurement not found for video {video_id}')


@router.patch('/{video_id}/measurements/{id}/',
              response_model=MeasurementSchema)
def modify_video(video_id: int,
                 id: int,
                 params: UpdateMeasurementAPI,
                 current_user: UserSchema =
                 Depends(get_current_active_user)) -> MeasurementSchema:
    measurement = video_manager.get_measurement(measurement_id=id)
    if measurement.video_id == video_id:
        return video_manager.update_measurement(measurement_id=id,
                                                     params=params)
    raise_http_exception(404, f'Measurement not found for video {video_id}')


@router.delete('/{video_id}/measurements/{id}/',
               response_model=MeasurementSchema)
def deactivate_video(video_id: int,
                     id: int,
                     current_user: UserSchema =
                     Depends(get_current_active_user)) -> MeasurementSchema:
    measurement = video_manager.get_measurement(measurement_id=id)
    if measurement.video_id == video_id:
        return video_manager.remove_measurement(measurement_id=id)
    raise_http_exception(404, f'Measurement not found for video {video_id}')
