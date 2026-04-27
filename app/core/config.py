from __future__ import annotations

from functools import lru_cache

from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PrintManager Pro"
    api_prefix: str = "/api/v1"
    environment: str = "development"

    database_url: str = "sqlite:///./printmanager.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ]
    )
    auto_create_tables: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
