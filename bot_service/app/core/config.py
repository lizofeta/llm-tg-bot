from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl

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

    # telegram
    telegram_bot_token: str

    # jwt
    jwt_secret: str
    jwt_alg: str

    # cache
    redis_url: AnyUrl

    # broker 
    rabbitmq_url: AnyUrl

    # OpenRouter
    openrouter_api_key: str
    openrouter_base_url: AnyUrl
    openrouter_model: str
    openrouter_site_url: AnyUrl
    openrouter_app_name: str

    # auth service
    auth_service_url: AnyUrl

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
