from abc import ABC, abstractmethod
from shared.schemas.videos import UpdateVideoAPI
from shared.schemas.measurements import UpdateMeasurementAPI
from shared.service.videos import VideoManager
from shared.queue.queue import q


class GenericOrchestrator(ABC):
    ORIGIN_QUEUE: str
    WIP_QUEUE: str
    ERROR_QUEUE: str

    def __init__(self) -> None:
        self.manager = VideoManager()
        self.run_service()

    def get_next_task(self):
        task = q.rpoplpush(self.ORIGIN_QUEUE, self.WIP_QUEUE)
        if task:
            return int(task)
    
    def remove_complete_task(self):
        q.lpop(self.WIP_QUEUE)
    
    def send_task_to_error(self, task_type: str):
        instance_id = int(q.rpoplpush(self.WIP_QUEUE, self.ERROR_QUEUE))
        task_types = {
            'video': (UpdateVideoAPI, self.manager.update_video),
            'measurement': (UpdateMeasurementAPI, self.manager.update_measurement)
        }
        schema, func = task_types.get(task_type, None)
        if schema:
            params = schema(status='ERROR')
            func(instance_id, params)

    def run_service(self):
        while True:
            self.process_task()

    @abstractmethod
    def process_task(self):
        pass
