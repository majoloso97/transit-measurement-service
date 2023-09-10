from shared.shared_settings import SharedSettings


class Settings(SharedSettings):
    MODEL_NAME: str = 'yolov8n.pt'
    MAX_FPS: int = 15
    MAX_BASE_DIMENSION: int = 360


settings = Settings() 
