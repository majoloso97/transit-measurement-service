import os
import logging
import numpy as np
import supervision as sv
from supervision.utils.video import VideoInfo, VideoSink
from core.model import model
from shared.database.crud import CRUDManager
from shared.database.models import Video
from shared.schemas.videos import (VideoSchema,
                                   NewVideo,
                                   UpdateVideoMetadata,
                                   FrameDetection)


logger = logging.getLogger(__name__)


class VideoProcessor:
    ALLOWED_CLASS_ID = [1, 2, 3, 5, 7]

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
        self.box_annotator = self.get_box_annotator()
        width = self.video.width
        height = self.video.height
        orient = 'horizontal'
        self.global_annotator = self.get_line_annotator(width,
                                                        height,
                                                        orient)
        self.class_annotators = {
            class_id: self.get_line_annotator(width, height, orient)
            for class_id in self.ALLOWED_CLASS_ID
        }

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

    def predict_from_frame(self): #TBD
        vid_generator = sv.get_video_frames_generator(self.path)
        iterator = iter(vid_generator)
        for _ in range(100):
            frame = next(iterator)
        return frame

    def predict(self):
        video_info = VideoInfo(width=self.video.width,
                               height=self.video.height,
                               fps=self.video.fps,
                               total_frames=self.video.total_frames)
        target_path = f'{self.video.path[:-4]}_processed.mp4'
        
        with VideoSink(target_path, video_info) as sink:
            for result in model.track(source=self.video.path, stream=True):
                frame = result.orig_img
                detections = sv.Detections.from_yolov8(result)

                if result.boxes.id is not None:
                    detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)

                # detections = filter(lambda d: d.class_id in self.ALLOWED_CLASS_ID,
                #                     detections)

                labels = [
                    f"{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
                    for *_, confidence, class_id, tracker_id
                    in detections
                ]

                # frame = self.box_annotator.annotate(
                #     scene=frame, 
                #     detections=detections,
                #     labels=labels
                # )
                counter, annotator = self.global_annotator
                counter.trigger(detections=detections)
                annotator.annotate(frame=frame, line_counter=counter)
                self.classify_detections(frame, detections)
                progress = {model.model.names.get(k): (v[0].in_count, v[0].out_count)
                            for k, v in self.class_annotators.items()}
                logger.info(progress)
                # Update progress to queue
                sink.write_frame(frame)

    def classify_detections(self, frame: np.ndarray,
                            detections: sv.Detections):
        for class_id, annotation_classes in self.class_annotators.items():
            counter, annotator = annotation_classes
            class_detections = self.extract_class_detections(detections,
                                                             class_id)
            counter.trigger(detections=class_detections)
            # annotator.annotate(frame=frame, line_counter=counter)

    def extract_class_detections(self,
                                 detections: sv.Detections,
                                 class_id: int) -> sv.Detections:
        class_mask = (detections.class_id == class_id)
        
        filtered_detections = sv.Detections(
            xyxy=detections.xyxy[class_mask],
            confidence=detections.confidence[class_mask],
            class_id=detections.class_id[class_mask],
            mask=detections.mask[class_mask] if not detections.mask is None else None,
            tracker_id=detections.tracker_id[class_mask] if not detections.tracker_id is None else None)
        return filtered_detections

    def get_box_annotator(self):
        # TODO: Adjust parameters dynamically to video size
        # thickness = video_height % 720
        box_annotator = sv.BoxAnnotator(
            thickness=1,
            text_thickness=1,
            text_scale=0.75
        )
        return box_annotator
    
    def get_line_annotator(self,
                           video_width: int,
                           video_height: int,
                           orient: str):
        # TODO: make this line generation dynamic
        start, end = self._get_line_points(video_width,
                                           video_height,
                                           'horizontal')
        line_counter = sv.LineZone(start=start, end=end)
        line_annotator = sv.LineZoneAnnotator(thickness=2,
                                              text_thickness=1,
                                              text_scale=0.5)
        return line_counter, line_annotator

    def _get_line_points(self,
                         video_width: int,
                         video_height: int,
                         orient: str):
        if orient == 'vertical':
            start = sv.Point(int(video_width/2), 0)
            end = sv.Point(int(video_width/2), video_height)
            return start, end
        
        if orient == 'horizontal':
            # start = sv.Point(0, int(video_height/2))
            # end = sv.Point(video_width, int(video_height/2))
            end = sv.Point(0, 100)
            start = sv.Point(video_width, 100)
            return start, end
