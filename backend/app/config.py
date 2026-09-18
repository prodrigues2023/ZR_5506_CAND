"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API service."""

    app_name: str = "Interactive TV Series Experience"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://localhost:5432/series"
    tvmaze_base_url: AnyHttpUrl = "http://api.tvmaze.com"
    huggingface_api_key: str | None = None
    huggingface_model: str = "google/flan-t5-base"
    huggingface_api_url: AnyHttpUrl = "https://api-inference.huggingface.co/models"
    anonymous_user_cookie: str = "series_user_id"
    cors_origins: list[str] = ["http://localhost:7777", "http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SERIES_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings instance for the process."""

    return Settings()
