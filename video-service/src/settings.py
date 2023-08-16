from shared.shared_settings import SharedSettings


class Settings(SharedSettings):
    MODEL_NAME: str = 'yolov8n.pt'


settings = Settings() 
