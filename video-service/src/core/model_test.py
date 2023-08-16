import logging
import numpy as np
import supervision as sv
from ultralytics import YOLO
from .image_sink import ImageSink


LINE_START = sv.Point(0, 360)
LINE_END = sv.Point(1280, 360)


def main():
    generator = sv.get_video_frames_generator('src/core/assets/vid.mp4')
    # create instance of BoxAnnotator
    box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.75)
    # acquire first video frame
    iterator = iter(generator)
    for _ in range(100):
        frame = next(iterator)

    # line_counter = LineZone(start=LINE_START, end=LINE_END)
    # line_annotator = LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
    # box_annotator = BoxAnnotator(
    #     thickness=2,
    #     text_thickness=1,
    #     text_scale=0.5
    # )

    model = YOLO("yolov8l.pt")
    CLASS_NAMES_DICT = model.model.names
        
    results = model(frame)
    logging.info('---- xyxy ----')
    logging.info(results[0].boxes.xyxy.cpu().numpy())
    logging.info('-- len --')
    logging.info(len(results[0].boxes.xyxy.cpu().numpy()))
    logging.info('---- confidence ----')
    logging.info(results[0].boxes.conf.cpu().numpy())
    logging.info('-- len --')
    logging.info(len(results[0].boxes.conf.cpu().numpy()))
    logging.info('---- class_id ----')
    logging.info(results[0].boxes.cls.cpu().numpy().astype(int))
    logging.info('-- len --')
    logging.info(len(results[0].boxes.cls.cpu().numpy().astype(int)))
    # detections = sv.Detections(
    #     xyxy=results[0].boxes.xyxy.cpu().numpy(),
    #     confidence=results[0].boxes.conf.cpu().numpy(),
    #     class_id=results[0].boxes.cls.cpu().numpy().astype(int)
    # )
    # # format custom labels
    # labels = [
    #     f"{CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
    #     for _, confidence, class_id, tracker_id
    #     in detections
    # ]
    # # annotate and display frame
    # frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
    # with ImageSink(target_dir_path='src/core/assets') as sink:
    #     sink.save_image(image=frame, image_name='predicted.png')
