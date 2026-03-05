from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # =========================
    # APP
    # =========================
    APP_NAME: str = "BoxRota"

    # development | production
    APP_ENV: str = "development"

    # URL pública do backend
    APP_URL: str = "http://localhost:8000"

    # =========================
    # CORS
    # =========================
    # múltiplos domínios separados por vírgula
    CORS_ORIGINS: str = "http://localhost:5173"

    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # =========================
    # DATABASE
    # =========================
    DATABASE_URL: str

    # =========================
    # JWT
    # =========================
    JWT_SECRET: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    SECRET_KEY: Optional[str] = None

    JWT_ALGORITHM: str = "HS256"

    # Access token (curto)
    JWT_ACCESS_EXPIRES_MIN: int = 30

    # Refresh token (longo)
    JWT_REFRESH_EXPIRES_DAYS: int = 30

    # =========================
    # PASSWORD
    # =========================
    PASSWORD_HASH_SCHEME: str = "bcrypt"

    # =========================
    # KIWIFY
    # =========================
    KIWIFY_WEBHOOK_SECRET: str = "change_me_kiwify_secret"

    # =========================
    # JWT SECRET RESOLVER
    # =========================
    def get_jwt_secret(self) -> str:
        """
        Resolve automaticamente qual secret usar.
        Prioridade:
        1. JWT_SECRET_KEY
        2. JWT_SECRET
        3. SECRET_KEY
        """

        secret = (
            self.JWT_SECRET_KEY
            or self.JWT_SECRET
            or self.SECRET_KEY
        )

        if not secret:
            raise RuntimeError(
                "JWT secret não configurado. "
                "Defina JWT_SECRET_KEY ou JWT_SECRET ou SECRET_KEY."
            )

        return secret

    # =========================
    # HELPERS
    # =========================
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    def is_development(self) -> bool:
        return self.APP_ENV.lower() == "development"


settings = Settings()