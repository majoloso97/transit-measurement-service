from redis import Redis
from settings import settings


class Queue(Redis):
    def __init__(self):
        super().__init__(host=settings.REDIS_HOST,
                       port=settings.REDIS_PORT,
                       password=settings.REDIS_PASSWORD)


q = Queue()
