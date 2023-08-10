import logging
from typing import Callable
from fastapi import FastAPI
from database.models import printing


def start_handler(app: FastAPI) -> Callable:
    '''Things to do while starting the API server'''
    async def start_app() -> None:
        logging.warning(printing())

    return start_app
