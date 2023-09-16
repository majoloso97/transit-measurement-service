import time
import logging
from settings import settings
from shared.queue.queue import q
from shared.schemas.measurements import UpdateMeasurementAPI
from orchestrators.generic_orchestrator import GenericOrchestrator
from core.optimizer import VideoOptimizer


logger = logging.getLogger(__name__)


class OptimizerOrchestrator(GenericOrchestrator):
    ORIGIN_QUEUE = 'VIDEO_TODO'
    WIP_QUEUE = 'VIDEO_WIP'
    ERROR_QUEUE = 'VIDEO_ERROR'

    def __init__(self) -> None:
        super().__init__()

    def process_task(self):
        video_id = self.get_next_task()
        if not video_id:
            logger.info("No videos in queue. Awaiting videos.")
            time.sleep(settings.THREAD_ORCHESTRATOR_SLEEP_TIME)
            return
        try:
            logger.info(f"Optimizing video ID {video_id}")
            optimizer = VideoOptimizer(video_id)
            optimizer.optimize()
            self.remove_complete_task()
            self.enqueue_measurment_tasks(video_id)
        except Exception as e:
            logger.warning(e)
            self.send_task_to_error('video')

    def enqueue_measurment_tasks(self, video_id: int):
        video = self.manager.get_video(video_id)
        if video.measurements:
            for measurement in video.measurements:
                if measurement.status == 'REQUESTED':
                    params = UpdateMeasurementAPI(status='QUEUED')
                    self.manager.update_measurement(measurement.id,
                                                    params)
                    q.lpush('MEASUREMENTS_TODO', measurement.id)
