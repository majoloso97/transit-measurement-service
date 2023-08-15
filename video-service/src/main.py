import time
import logging
from core.checks import get_ultralytics_checks


logging.root.setLevel(logging.INFO)


def run_video_service():
    get_ultralytics_checks()
    while True:
        logging.info('Running Video Service')
        time.sleep(60)


if __name__ == "__main__":
    run_video_service()
