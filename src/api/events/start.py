from typing import Callable
from fastapi import FastAPI
from core.checks import get_ultralytics_checks


def start_handler(app: FastAPI) -> Callable:
    '''Things to do while starting the API server'''
    async def start_app() -> None:
        get_ultralytics_checks()

    return start_app
