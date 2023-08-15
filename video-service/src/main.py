import time
import logging
from settings import settings
from core.checks import get_ultralytics_checks
from shared.database.db import db
from shared.queue.queue import q


logging.root.setLevel(logging.getLevelName(settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


def run_video_service():
    get_ultralytics_checks()
    if not db.is_active:
        raise ConnectionError('Database not connected')
    if not q.ping():
        raise ConnectionError('Database not connected')
    logger.info('Postgres database connected')
    logger.info('Redis queue connected')
    while True:
        logging.info('Running Video Service')
        time.sleep(60)


if __name__ == "__main__":
    run_video_service()
