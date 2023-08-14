from shared.shared_settings import SharedSettings


class Settings(SharedSettings):
    FAST_API_KEY: str
    LOG_LEVEL: str = 'INFO'
    AUTO_RELOAD: bool = False


settings = Settings() 
