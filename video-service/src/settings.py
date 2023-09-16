from shared.shared_settings import SharedSettings


class Settings(SharedSettings):
    MODEL_NAME: str = 'yolov8n.pt'
    MAX_FPS: int = 15
    MAX_BASE_DIMENSION: int = 360
    ALLOWED_CLASS_ID: list = [1, 2, 3, 5, 7]
    CONFIDENCE_THRESHOLD: float = 0
    THREAD_ORCHESTRATOR_SLEEP_TIME: int = 0


settings = Settings() 
