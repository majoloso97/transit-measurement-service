from fastapi import APIRouter, Depends
from api.dependencies.auth import get_current_active_user, decode_token
from shared.schemas.videos import VideoSchema, NewVideo, UpdateVideoAPI
from shared.database.crud import CRUDManager
from shared.database.models import Video


router = APIRouter(prefix='/api/v1/videos')
video_manager = CRUDManager(db_model=Video,
                            pydantic_create=NewVideo,
                            pydantic_update=UpdateVideoAPI,
                            pydantic_response=VideoSchema)


@router.post('/')
def create_video(video: NewVideo) -> VideoSchema:
    return video_manager.create_item(video)


@router.get('/{id}/', response_model=VideoSchema)
def get_user(id: str,
             valid_token=Depends(decode_token)) -> VideoSchema:
    return video_manager.get_item(id=id)


@router.patch('/{id}/', response_model=VideoSchema)
def modify_user(id: str,
                params: UpdateVideoAPI,
                valid_token=Depends(decode_token)):
    return video_manager.update_item(item_id=id,
                                     item_update=params)


@router.delete('/{id}/', response_model=VideoSchema)
async def deactivate_user(id: str,
                          valid_token=Depends(decode_token)):
    params = UpdateVideoAPI(is_active=False)
    return video_manager.update_item(item_id=id,
                                     item_update=params)
