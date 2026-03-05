from __future__ import annotations

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "BoxRota"
    ENV: str = Field(default="local")

    DATABASE_URL: str = Field(default="postgresql+psycopg://boxrota:boxrota@db:5432/boxrota")

    JWT_SECRET: str = Field(default="change-me")
    JWT_ACCESS_TTL_MINUTES: int = Field(default=30)
    JWT_REFRESH_TTL_DAYS: int = Field(default=30)

    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)

    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()