from fastapi import APIRouter, Depends
from api.dependencies.auth import get_current_active_user
from shared.schemas.videos import VideoSchema, NewVideo, UpdateVideoAPI
from shared.schemas.users import UserSchema
from shared.database.crud import CRUDManager
from shared.database.models import Video


router = APIRouter(prefix='/api/v1/videos')
video_manager = CRUDManager(db_model=Video,
                            pydantic_create=NewVideo,
                            pydantic_update=UpdateVideoAPI,
                            pydantic_response=VideoSchema)


@router.post('/')
def create_video(video: NewVideo,
                 current_user: UserSchema =
                 Depends(get_current_active_user)) -> VideoSchema:
    # TODO: Upload and get S3 path
    video.owner_id = current_user.id
    saved = video_manager.create_item(video)
    # TODO: Add video to queue
    return saved


@router.get('/{id}/', response_model=VideoSchema)
def get_user(id: str,
             current_user: UserSchema =
             Depends(get_current_active_user)) -> VideoSchema:
    return video_manager.get_item(id=id)


@router.patch('/{id}/', response_model=VideoSchema)
def modify_user(id: str,
                params: UpdateVideoAPI,
                current_user: UserSchema =
                Depends(get_current_active_user)):
    return video_manager.update_item(item_id=id,
                                     item_update=params)


@router.delete('/{id}/', response_model=VideoSchema)
async def deactivate_user(id: str,
                          current_user: UserSchema =
                          Depends(get_current_active_user)):
    params = UpdateVideoAPI(is_active=False)
    return video_manager.update_item(item_id=id,
                                     item_update=params)
