from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    LOG_LEVEL: str = 'INFO'
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    AWS_REGION: str
    AWS_KEY_ID: str
    AWS_SECRET: str
