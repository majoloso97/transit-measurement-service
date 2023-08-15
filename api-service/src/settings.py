from shared.shared_settings import SharedSettings


class Settings(SharedSettings):
    FAST_API_KEY: str
    AUTO_RELOAD: bool = False


settings = Settings() 
