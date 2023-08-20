from shared.shared_settings import SharedSettings


class Settings(SharedSettings):
    SECRET_APP_KEY: str
    TOKEN_EXPIRATION: int
    JWT_ALGORITHM: str


settings = Settings() 
