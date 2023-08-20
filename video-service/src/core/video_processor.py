import os
from supervision import get_video_frames_generator
from supervision.utils.video import VideoInfo
from shared.database.db import db
from shared.database.models import Video
from core.types import VideoMetadata
from core.model import model


class VideoProcessor:
    def __init__(self, video_path: str) -> None:
        is_valid = self._validate_video_path(video_path)
        if is_valid:
            self.path = video_path
            self.metadata = self.get_video_metadata(video_path)

    def get_video_metadata(self, video_metadata):
        sv_metadata = VideoInfo.from_video_path(video_metadata)
        metadata = VideoMetadata(width=sv_metadata.width,
                                 height=sv_metadata.height,
                                 fps=sv_metadata.fps,
                                 total_frames=sv_metadata.total_frames)
        return metadata

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
