from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "AutoDesk Kiwi API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///data.db"
    
    # CORS (only for development - restrict in production)
    cors_origins: list[str] = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ]
    
    # External APIs
    user_agent: str = "AutoDeskKiwi/1.0 (kiwi-app-local-dev)"
    api_timeout: float = 12.0
    
    # Hyperplanning
    hyperplanning_url: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env variables not defined in Settings

@lru_cache()
def get_settings():
    return Settings()