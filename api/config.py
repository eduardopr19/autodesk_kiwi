from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AutoDesk Kiwi API"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str = "sqlite:///data.db"

    cors_origins: list[str] = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ]

    user_agent: str = "AutoDeskKiwi/1.0 (kiwi-app-local-dev)"
    api_timeout: float = 12.0

    hyperplanning_url: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache
def get_settings():
    return Settings()
