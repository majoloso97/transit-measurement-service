import sys
import time
import logging
from core.checks import get_ultralytics_checks
from core.optimizer import VideoOptimizer
from core.processor import VideoProcessor
from shared.database.db import db
from shared.queue.queue import q
from shared.aws.factory import AWSServiceFactory
import cv2
from supervision.utils.video import VideoInfo, VideoSink


def run_video_service(logger: logging.Logger):
    if not db.is_active:
        raise ConnectionError('Postgres database not connected')
    if not q.ping():
        raise ConnectionError('Redis queue not connected')
    logger.info('Postgres database connected')
    logger.info('Redis queue connected')
    get_ultralytics_checks()
    s3 = AWSServiceFactory.get_service(service='s3',
                                       config= {'bucket_name': 'transit-ventures-test'})
    url_opt = s3.generate_presigned_url('my_video_opt.mp4')
    url = s3.get_presigned_url('my_video.mp4')
    
    info = VideoInfo.from_video_path(url)
    logging.warning(f'INFO: {info}')
    
    vidcap = cv2.VideoCapture(url)
    with VideoSink('src/core/assets/test.mp4', info) as sink:
        for _ in range(100):
            success, frame = vidcap.read()
            if not success: break
            sink.write_frame(frame)

    while True:
        logger.info('Running Video Service')
        try:
            # TODO: Check queue
            # TODO: Start video processing
            time.sleep(600)
        except:
            logger.warning(f'Ending video service process')
            sys.exit(0)
