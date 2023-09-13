import sys
import time
import logging
from core.checks import get_ultralytics_checks
# from core.optimizer import VideoOptimizer
# from core.predictor import VideoPredictor
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
    # vid = VideoOptimizer(video_id=11)
    # vid.optimize()
    # vid = VideoPredictor(measurement_id=3)
    # vid.predict()
    
    while True:
        logger.info('Running Video Service')
        try:
            # TODO: Check queue
            # TODO: Start video processing
            time.sleep(600)
        except:
            logger.warning(f'Ending video service process')
            sys.exit(0)
