import threading
import logging
from core.checks import get_ultralytics_checks
from orchestrators import OptimizerOrchestrator, PredictorOrchestrator
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

    optimization_thread = threading.Thread(target=OptimizerOrchestrator)
    prediction_thread = threading.Thread(target=PredictorOrchestrator)

    optimization_thread.start()
    prediction_thread.start()

    optimization_thread.join()
    prediction_thread.join()
