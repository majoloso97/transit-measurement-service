import os
import logging
from watchfiles import run_process
from settings import settings
from log_config import setup_logger
from service import run_video_service


setup_logger(logging.root)
logger = logging.getLogger('main')


def autoreload_callback(changes):
    msg = 'Changes detected in {file_name}'
    filename = list(changes)[0][1]
    logger.info(msg.format(file_name=filename))
    logger.info('Auto-reloading process')


if __name__ == "__main__":
    if settings.AUTO_RELOAD:
        logger.info(f'Auto-reload is on. Will watch files in {os.getcwd()}')
        run_process('.',
                    target=run_video_service,
                    args=(logger,),
                    callback=autoreload_callback)
    else:
        run_video_service(logger)
