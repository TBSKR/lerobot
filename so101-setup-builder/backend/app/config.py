from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://postgres:postgres@db:5432/so101_builder"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # API Keys
    gemini_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    serpapi_key: Optional[str] = None

    # App settings
    app_name: str = "SO-101 Setup Builder"
    debug: bool = True
    session_expiry_days: int = 30

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5180", "http://127.0.0.1:5173", "http://127.0.0.1:5180"]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
