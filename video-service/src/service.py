import os
import sys
import time
import logging
from core.checks import get_ultralytics_checks
from core.processor import VideoProcessor
from shared.database.db import db
from shared.queue.queue import q


def run_video_service(logger: logging.Logger):
    if not db.is_active:
        raise ConnectionError('Postgres database not connected')
    if not q.ping():
        raise ConnectionError('Redis queue not connected')
    logger.info('Postgres database connected')
    logger.info('Redis queue connected')
    get_ultralytics_checks()
    vid = VideoProcessor(video_id=2)
    vid.predict()
    while True:
        logger.info('Running Video Service')
        try:
            # TODO: Check queue
            # TODO: Start video processing
            time.sleep(600)
        except:
            logger.warning(f'Ending video service process')
            sys.exit(0)
