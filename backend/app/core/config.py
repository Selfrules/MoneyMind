"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    api_title: str = "MoneyMind API"
    api_version: str = "1.0.0"
    api_description: str = "AI-First Personal Finance Coach API"

    # CORS Settings
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ]

    # Database
    database_path: str = "../data/moneymind.db"

    # AI Settings
    anthropic_api_key: str = ""

    # Debug
    debug: bool = True

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
