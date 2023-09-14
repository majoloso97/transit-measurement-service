import os
import logging
import numpy as np
import supervision as sv
from supervision.utils.video import VideoInfo, VideoSink
from settings import settings
from core.model import model
from shared.service.videos import VideoManager
from shared.schemas.videos import VideoSchema
from shared.schemas.measurements import (MeasurementSchema,
                                         UpdateMeasurementInternal,
                                         DetectionSchema)


logger = logging.getLogger(__name__)


class VideoPredictor:
    ALLOWED_CLASS_ID = settings.ALLOWED_CLASS_ID
    CONFIDENCE_THRESHOLD = settings.CONFIDENCE_THRESHOLD

    def __init__(self, measurement_id: int) -> None:
        self.manager = VideoManager('internal')
        if not isinstance(measurement_id, int):
            raise TypeError('Measurement ID should be integer')

        self.measurement: MeasurementSchema = self.manager.get_measurement(measurement_id)
        self._get_video_metadata()
        self._instantiate_annotators()

    def _get_video_metadata(self):
        video: VideoSchema = self.manager.get_video(self.measurement.video_id)
        self.video_url = video.optimized_video_url
        self.video_duration = video.duration
        self.video_info = VideoInfo.from_video_path(self.video_url)
        
        status = UpdateMeasurementInternal(status='PROCESSING')
        self.measurement = self.manager.update_measurement(self.measurement.id,
                                                           status)

    def _instantiate_annotators(self):
        self.box_annotator = self._get_box_annotator()
        self._get_line_points()
        self.global_annotator = self._get_line_annotator()
        self.class_annotators = {
            class_id: self._get_line_annotator()
            for class_id in self.ALLOWED_CLASS_ID
        }

    def _get_box_annotator(self):
        # TODO: Adjust parameters dynamically to video size
        # thickness = video_height % 720
        box_annotator = sv.BoxAnnotator(
            thickness=1,
            text_thickness=1,
            text_scale=0.75
        )
        return box_annotator

    def _get_line_annotator(self):
        start, end = self._line_start, self._line_end
        line_counter = sv.LineZone(start=start, end=end)
        line_annotator = sv.LineZoneAnnotator(thickness=2,
                                              text_thickness=1,
                                              text_scale=0.5)
        return line_counter, line_annotator

    def _get_line_points(self):
        x1 = int(self.video_info.width * self.measurement.x1)
        y1 = int(self.video_info.height * self.measurement.y1)
        x2 = int(self.video_info.width * self.measurement.x2)
        y2 = int(self.video_info.height * self.measurement.y2)
        self._line_start = sv.Point(x1, y1)
        self._line_end = sv.Point(x2, y2)

    def predict(self):
        target_s3_key = self.manager.generate_video_key('output')
        local_filename = target_s3_key.split("/")[-1]
        # _target_path is raw mp4, target_path is the file for web codec 
        _target_path = f'/app/src/core/assets/_{local_filename}'
        target_path = f'/app/src/core/assets/{local_filename}'

        self.generate_predicted_video(_target_path)

        is_valid_in_filesystem = os.path.isfile(_target_path)
        if not is_valid_in_filesystem:
            raise ValueError('Target path is not a valid path')
        
        # Use ffmpeg to change codecs
        os.system(f"ffmpeg -y -i {_target_path} -vcodec libx264 -f mp4 {target_path}")
        self.manager.s3.upload_video_file(target_path, target_s3_key)
        os.remove(target_path)
        os.remove(_target_path)
        self.save_result_statistics(target_s3_key)

    def generate_predicted_video(self, target_path):
        with VideoSink(target_path, self.video_info) as sink:
            for result in model.track(source=self.video_url,
            # for result in model.track(source='/app/src/core/assets/vid2_optimized.mp4',
                                      stream=True):
                try:
                    frame = result.orig_img
                    detections = self.process_frame_detections(result)
                    labels = self.get_frame_labels(detections)

                    frame = self.box_annotator.annotate(
                        scene=frame, 
                        detections=detections,
                        labels=labels
                    )
                    self.count_and_annotate_class_detections(frame, detections)
                    counter, annotator = self.global_annotator
                    counter.trigger(detections=detections)
                    annotator.annotate(frame=frame, line_counter=counter)
                    # TODO: Update progress to queue
                    sink.write_frame(frame)
                except Exception:
                    continue
        
    def save_result_statistics(self, output_s3_key):
        global_count = 0
        for k, v in self.class_annotators.items():
            count = v[0].in_count + v[0].out_count
            global_count += count
            frequency = count/self.video_duration
            if count == 0:
                continue
            detection = DetectionSchema(
                class_name=model.model.names.get(k).upper(),
                count=count,
                frequency=frequency
            )
            self.manager.create_detection(self.measurement.id,
                                          detection)
        global_frequency = global_count/self.video_duration
        measurement = UpdateMeasurementInternal(
            status='PREDICTED',
            output_s3_key=output_s3_key,
            detections_count=global_count,
            global_frequency=global_frequency
        )
        self.manager.update_measurement(self.measurement.id,
                                        measurement)

    def process_frame_detections(self, result):
        detections = sv.Detections.from_yolov8(result)
        if result.boxes.id is not None:
            detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
        
        detections = detections[(np.isin(detections.class_id,
                                         self.ALLOWED_CLASS_ID))
                                & (detections.confidence > self.CONFIDENCE_THRESHOLD)]
        return detections

    def get_frame_labels(self, detections):
        labels = [
            f"{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
            for *_, confidence, class_id, tracker_id
            in detections
        ]
        return labels

    def count_and_annotate_class_detections(self,
                                            frame: np.ndarray,
                                            detections: sv.Detections):
        for class_id, annotation_classes in self.class_annotators.items():
            counter, annotator = annotation_classes
            class_detections = self.extract_class_detections(detections,
                                                             class_id)
            counter.trigger(detections=class_detections)
            annotator.annotate(frame=frame, line_counter=counter)

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
