from supervision.utils.video import VideoInfo
from core.model import model


class VideoProcessor:
    def __init__(self, video_path: str) -> None:
        self.path = video_path
        self.metadata = self.get_video_metadata()

    def get_video_metadata(self):
        self.metadata = VideoInfo.from_video_path(self.path)
