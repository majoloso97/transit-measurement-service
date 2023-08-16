import os
import sys
import time
import logging
from core.checks import get_ultralytics_checks
from core.video_processor import VideoProcessor
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
    path_vid = '/app/src/core/assets/vid.mp4'
    vid = VideoProcessor(path_vid)
    logger.info(vid.metadata.dict())
    while True:
        logger.info('Running Video Service')
        try:
            time.sleep(600)
        except:
            logger.warning(f'Ending video service process')
            sys.exit(0)
