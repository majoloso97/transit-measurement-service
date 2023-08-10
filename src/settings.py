from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODEL_NAME: str
    FAST_API_KEY: str
    LOG_LEVEL: str = 'INFO'
    AUTO_RELOAD: bool = False


settings = Settings() 
