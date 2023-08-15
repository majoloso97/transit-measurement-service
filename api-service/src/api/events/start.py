import logging
from typing import Callable
from fastapi import FastAPI
from shared.database.db import db
from shared.database.models import Video
from shared.queue.queue import q


logger = logging.getLogger(__name__)


def start_handler(app: FastAPI) -> Callable:
    '''Things to do while starting the API server'''
    async def start_app() -> None:
        if not db.is_active:
            raise ConnectionError('Database not connected')
        if not q.ping():
            raise ConnectionError('Database not connected')
        logger.info('Postgres database connected')
        logger.info('Redis queue connected')

    return start_app
