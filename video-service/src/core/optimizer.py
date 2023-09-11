import os
import logging
import cv2
from supervision.utils.video import VideoInfo, VideoSink
from settings import settings
from shared.service.videos import VideoManager
from shared.schemas.videos import (VideoSchema,
                                   UpdateVideoInternal)

MAX_FPS = settings.MAX_FPS
MAX_BASE_DIMENSION = settings.MAX_BASE_DIMENSION
logger = logging.getLogger(__name__)


class VideoOptimizer:
    def __init__(self, video_id: int) -> None:
        self.manager = VideoManager('internal')
        if not isinstance(video_id, int):
            raise TypeError('Video ID should be integer')
        
        self.video: VideoSchema = self.manager.get_video(video_id)
        is_valid = self._validate_video_path(self.video.input_video_url)
        if not is_valid:
            raise ValueError('Video path is not valid')
        
        self.save_metadata(self.video.input_video_url)

    def save_metadata(self, video_path):
        metadata = self.get_video_metadata(video_path)
        self.video = self.manager.update_video(video_id=self.video.id,
                                               params=metadata)
    
    def get_video_metadata(self, video_path):
        try:
            info = VideoInfo.from_video_path(video_path)
            duration = int(info.total_frames/info.fps)
            metadata = UpdateVideoInternal(status='OPTIMIZING',
                                           width=info.width,
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

        s3_prefix = 'https://s3.amazonaws.com/transit-ventures-test/videos'
        is_s3_url = video_path.startswith(s3_prefix)
        if not is_s3_url:
            raise ValueError('Returned string is not a valid path')

        return True
    
    def optimize(self):
        video_info = VideoInfo(width=self.video.width,
                               height=self.video.height,
                               fps=self.video.fps,
                               total_frames=self.video.total_frames)
        target_s3_key = self.manager.generate_video_key('optimized')
        local_filename = target_s3_key.split("/")[-1]
        # _target_path is raw mp4, target_path is the file for web codec 
        _target_path = f'/app/src/core/assets/_{local_filename}'
        target_path = f'/app/src/core/assets/{local_filename}'
        
        processor, kwargs = self.get_processor_and_args(video_info)
        processor(_target_path, **kwargs)

        is_valid_in_filesystem = os.path.isfile(_target_path)
        if not is_valid_in_filesystem:
            raise ValueError('Target path is not a valid path')

        # Use ffmpeg to change codecs
        os.system(f"ffmpeg -y -i {_target_path} -vcodec libx264 -f mp4 {target_path}")
        fps_factor = kwargs.get('fps_factor', 1)
        added_metadata = UpdateVideoInternal(optimized_s3_key=target_s3_key,
                                             optimized_fps_ratio=fps_factor)
        self.video = self.manager.update_video(video_id=self.video.id,
                                               params=added_metadata,
                                               add_upload_url=True,
                                               key_from='optimized_s3_key')
        self.manager.s3.upload_video_file(target_path, target_s3_key)
        os.remove(target_path)
        os.remove(_target_path)


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
            kwargs = {
                'video_info': new_video_info,
                'target_dimensions': new_dimensions,
                'fps_factor': fps_factor,
            }
            return self.trim_video_fps_and_rescale, kwargs

        if is_bigger:
            new_dimensions = self.get_target_dimensions(dimensions,
                                                        min_side_size)
            new_video_info = VideoInfo(width=new_dimensions[0],
                                       height=new_dimensions[1],
                                       fps=self.video.fps,
                                       total_frames=self.video.total_frames)
            kwargs = {
                'video_info': new_video_info,
                'target_dimensions': new_dimensions,
            }
            return self.rescale_video, kwargs

        if higher_fps:
            fps_factor = MAX_FPS / self.video.fps
            new_video_info = VideoInfo(width=self.video.width,
                                       height=self.video.height,
                                       fps=MAX_FPS,
                                       total_frames=self.video.total_frames)
            kwargs = {
                'video_info': new_video_info,
                'fps_factor': fps_factor,
            }
            return self.trim_video_fps, kwargs

        kwargs = {
                'video_info': video_info,
            }
        return self.copy_video, kwargs
    
    def get_target_dimensions(self, video_dimensions, min_side):
        crop_factor = MAX_BASE_DIMENSION/min_side
        new_width = int(video_dimensions[0]*crop_factor)
        new_height = int(video_dimensions[1]*crop_factor)
        return new_width, new_height
    
    def copy_video(self, target_path, video_info):
        vidcap = cv2.VideoCapture(self.video.input_video_url)
        count = 0
        success = True
        with VideoSink(target_path, video_info) as sink:
            while success:
                success, frame = vidcap.read()
                if not success: break
                sink.write_frame(frame)
                count += 1

    def trim_video_fps(self, target_path, video_info, fps_factor):
        with VideoSink(target_path, video_info) as sink:
            vidcap = cv2.VideoCapture(self.video.input_video_url)
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
        vidcap = cv2.VideoCapture(self.video.input_video_url)
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
            vidcap = cv2.VideoCapture(self.video.input_video_url)
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
