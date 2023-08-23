import os
from supervision import get_video_frames_generator
from supervision.utils.video import VideoInfo
from core.model import model
from shared.database.crud import CRUDManager
from shared.database.models import Video
from shared.schemas.videos import (VideoSchema,
                                   NewVideo,
                                   UpdateVideoMetadata,
                                   FrameDetection)


class VideoProcessor:
    def __init__(self, video_id: int) -> None:
        self.crud = CRUDManager(db_model=Video,
                                pydantic_create=NewVideo,
                                pydantic_update=UpdateVideoMetadata,
                                pydantic_response=VideoSchema)
        if isinstance(video_id, int):
            self.video = self.crud.get_item(video_id)
            is_valid = self._validate_video_path(self.video.path)
            if is_valid:
                self.save_metadata(self.video.path)

    def save_metadata(self, video_path):
        metadata = self.get_video_metadata(video_path)
        self.crud.update_item(item_id=self.video.id,
                              item_update=metadata)
    
    def get_video_metadata(self, video_path):
        try:
            sv_metadata = VideoInfo.from_video_path(video_path)
            duration = int(sv_metadata.total_frames/sv_metadata.fps)
            metadata = UpdateVideoMetadata(width=sv_metadata.width,
                                           height=sv_metadata.height,
                                           fps=sv_metadata.fps,
                                           total_frames=sv_metadata.total_frames,
                                           duration=duration)
            return metadata
        except:
            raise RuntimeError('Video metadata could not be extracted')

    def _validate_video_path(self, video_path: str) -> bool:
        if not isinstance(video_path, str):
            raise TypeError('Video path should be a string')

        is_valid_in_filesystem = os.path.isfile(video_path)
        if not is_valid_in_filesystem:
            raise ValueError('Returned string is not a valid path')

        return True

    def predict_from_frame(self):
        vid_generator = get_video_frames_generator(self.path)
        iterator = iter(vid_generator)
        for _ in range(100):
            frame = next(iterator)
        return frame

    def process_frame_detections(self, frame):
        results = model(frame)
