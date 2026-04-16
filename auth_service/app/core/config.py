from pydantic_settings import BaseSettings, SettingsConfigDict 
from functools import lru_cache

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False
    )

    # app
    app_name: str 
    env: str

    # JWT
    jwt_secret: str 
    jwt_alg: str 
    access_token_expire_minutes: int = 60

    # DB
    sqlite_path: str

@lru_cache
def get_settings() -> Settings:
    return Settings()

def get_db_url(settings: Settings) -> str:
    return f"sqlite+aiosqlite:///{settings.sqlite_path}"
