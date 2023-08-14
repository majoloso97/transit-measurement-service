import logging
from typing import Callable
from fastapi import FastAPI
from redis import Redis
from shared.database.models import printing


def start_handler(app: FastAPI) -> Callable:
    '''Things to do while starting the API server'''
    async def start_app() -> None:
        r = Redis(host='transit_measurement_service_queue', password='admin')
        logging.info(r.ping())
        logging.info(printing())

    return start_app
