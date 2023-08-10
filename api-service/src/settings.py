from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FAST_API_KEY: str
    LOG_LEVEL: str = 'INFO'
    AUTO_RELOAD: bool = False


settings = Settings() 
