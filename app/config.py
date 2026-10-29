import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    APP_NAME: str = "Edupets"
    APP_ENV: str = os.getenv("VERCEL_ENV", "development")
    SECRET_KEY: str = "change-me-before-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    COOKIE_NAME: str = "edupets_session"
    COOKIE_SECURE: bool = os.getenv("VERCEL_ENV") in {"production", "preview"}
    CSRF_COOKIE_NAME: str = "edupets_csrf"

    DATABASE_URL: str = ""
    GEMINI_API_KEY: str = Field(default="", repr=False)

    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.APP_ENV.casefold() in {"production", "prod", "preview"}:
            if self.SECRET_KEY == "change-me-before-production" or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY debe ser un secreto privado de al menos 32 caracteres en producción.")
            if not self.COOKIE_SECURE:
                raise ValueError("COOKIE_SECURE debe estar activado en producción.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
