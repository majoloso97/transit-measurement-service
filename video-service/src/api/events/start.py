import logging
from typing import Callable
from fastapi import FastAPI
from database.models import printing
from core.checks import get_ultralytics_checks


def start_handler(app: FastAPI) -> Callable:
    '''Things to do while starting the API server'''
    async def start_app() -> None:
        get_ultralytics_checks()
        logging.warning(printing())

    return start_app
