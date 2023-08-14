from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PASSWORD: str
