import logging
from typing import Callable
from fastapi import FastAPI
from redis import Redis
from database.models import printing


def start_handler(app: FastAPI) -> Callable:
    '''Things to do while starting the API server'''
    async def start_app() -> None:
        r = Redis(password='admin')
        logging.info(r.ping())

    return start_app
