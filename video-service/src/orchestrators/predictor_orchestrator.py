import logging
from shared.queue.queue import q
from orchestrators.generic_orchestrator import GenericOrchestrator
from core.predictor import VideoPredictor


logger = logging.getLogger(__name__)


class PredictorOrchestrator(GenericOrchestrator):
    ORIGIN_QUEUE = 'MEASUREMENTS_TODO'
    WIP_QUEUE = 'MEASUREMENTS_WIP'
    ERROR_QUEUE = 'MEASUREMENTS_ERROR'

    def __init__(self) -> None:
        super().__init__()

    def process_task(self):
        measurement_id = self.get_next_task()
        if measurement_id:
            try:
                predictor = VideoPredictor(measurement_id)
                predictor.predict()
                self.remove_complete_task()
            except Exception as e:
                logger.warning(e)
                self.send_task_to_error('measurement')
