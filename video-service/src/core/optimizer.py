import os
import logging
import cv2
from supervision.utils.video import VideoInfo, VideoSink
from shared.database.crud import CRUDManager
from shared.database.models import Video
from shared.schemas.videos import (VideoSchema,
                                   NewVideo,
                                   UpdateVideoMetadata)

MAX_FPS = 15
MAX_BASE_DIMENSION = 360
logger = logging.getLogger(__name__)


class VideoOptimizer:
    def __init__(self, video_id: int) -> None:
        self.crud = CRUDManager(db_model=Video,
                                pydantic_create=NewVideo,
                                pydantic_update=UpdateVideoMetadata,
                                pydantic_response=VideoSchema)
        if not isinstance(video_id, int):
            raise TypeError('Video ID should be integer')
        
        self.video: VideoSchema = self.crud.get_item(video_id)
        is_valid = self._validate_video_path(self.video.path)
        if not is_valid:
            raise ValueError('Video path is not valid')
        
        self.save_metadata(self.video.path)

    def save_metadata(self, video_path):
        metadata = self.get_video_metadata(video_path)
        self.video = self.crud.update_item(item_id=self.video.id,
                                           item_update=metadata)
    
    def get_video_metadata(self, video_path):
        try:
            info = VideoInfo.from_video_path(video_path)
            duration = int(info.total_frames/info.fps)
            metadata = UpdateVideoMetadata(width=info.width,
                                           height=info.height,
                                           fps=info.fps,
                                           total_frames=info.total_frames,
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
    
    def optimize(self):
        video_info = VideoInfo(width=self.video.width,
                               height=self.video.height,
                               fps=self.video.fps,
                               total_frames=self.video.total_frames)
        target_path = f'{self.video.path[:-4]}_optimized.mp4'
        processor, args = self.get_processor_and_args(video_info)
        if processor:
            processor(target_path, *args)

    def get_processor_and_args(self, video_info: VideoInfo):
        dimensions = (video_info.width, video_info.height)
        min_side_size = min(dimensions)
        
        is_bigger = min_side_size > MAX_BASE_DIMENSION
        higher_fps = video_info.fps > MAX_FPS
        
        if is_bigger and higher_fps:
            new_dimensions = self.get_target_dimensions(dimensions,
                                                        min_side_size)
            fps_factor = MAX_FPS / self.video.fps
            new_video_info = VideoInfo(width=new_dimensions[0],
                                       height=new_dimensions[1],
                                       fps=MAX_FPS,
                                       total_frames=self.video.total_frames)
            return self.trim_video_fps_and_rescale, (new_video_info,
                                                     new_dimensions,
                                                     fps_factor)

        if is_bigger:
            new_dimensions = self.get_target_dimensions(dimensions,
                                                        min_side_size)
            new_video_info = VideoInfo(width=new_dimensions[0],
                                       height=new_dimensions[1],
                                       fps=self.video.fps,
                                       total_frames=self.video.total_frames)
            return self.rescale_video, (new_video_info, new_dimensions,)

        if higher_fps:
            fps_factor = MAX_FPS / self.video.fps
            new_video_info = VideoInfo(width=self.video.width,
                                       height=self.video.height,
                                       fps=MAX_FPS,
                                       total_frames=self.video.total_frames)
            return self.trim_video_fps, (new_video_info,
                                         fps_factor,)

        return None
    
    def get_target_dimensions(self, video_dimensions, min_side):
        crop_factor = MAX_BASE_DIMENSION/min_side
        new_width = int(video_dimensions[0]*crop_factor)
        new_height = int(video_dimensions[1]*crop_factor)
        return new_width, new_height

    def trim_video_fps(self, target_path, video_info, fps_factor):
        with VideoSink(target_path, video_info) as sink:
            vidcap = cv2.VideoCapture(self.video.path)
            assert vidcap.isOpened()
            index_in = -1
            index_out = -1

            while True:
                success = vidcap.grab()
                if not success: break
                index_in += 1

                out_due = int(index_in / fps_factor)
                if out_due > index_out:
                    success, frame = vidcap.retrieve()
                    if not success: break
                    index_out += 1
                    sink.write_frame(frame)

    def rescale_video(self, target_path, video_info, target_dimensions):
        vidcap = cv2.VideoCapture(self.video.path)
        count = 0
        success = True
        with VideoSink(target_path, video_info) as sink:
            while success:
                success, frame = vidcap.read()
                if not success: break
                resized = cv2.resize(frame, target_dimensions)
                sink.write_frame(resized)
                count += 1

    def trim_video_fps_and_rescale(self,
                                   target_path,
                                   video_info,
                                   target_dimensions,
                                   fps_factor):
        with VideoSink(target_path, video_info) as sink:
            vidcap = cv2.VideoCapture(self.video.path)
            assert vidcap.isOpened()
            index_in = -1
            index_out = -1

            while True:
                success = vidcap.grab()
                if not success: break
                index_in += 1

                out_due = int(index_in / fps_factor)
                if out_due > index_out:
                    success, frame = vidcap.retrieve()
                    if not success: break
                    resized = cv2.resize(frame, target_dimensions)
                    index_out += 1
                    sink.write_frame(resized)
