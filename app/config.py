import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    APP_NAME: str = "Edupets"
    APP_ENV: str = Field(default_factory=lambda: os.getenv("VERCEL_ENV") or "development")
    SECRET_KEY: str = Field(default="change-me-before-production", repr=False)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    COOKIE_NAME: str = "edupets_session"
    COOKIE_SECURE: bool = Field(
        default_factory=lambda: (os.getenv("VERCEL_ENV") or "").casefold() in {"production", "preview"}
    )
    CSRF_COOKIE_NAME: str = "edupets_csrf"

    DATABASE_URL: str = Field(default="", repr=False)
    GEMINI_API_KEY: str = Field(default="", repr=False)

    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        hide_input_in_errors=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
            return init_settings, env_settings, file_secret_settings
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    @field_validator("COOKIE_SECURE", mode="before")
    @classmethod
    def normalize_cookie_secure(cls, value: object) -> object:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().casefold()
            if normalized in {"true", "1"}:
                return True
            if normalized in {"false", "0"}:
                return False
            raise ValueError("COOKIE_SECURE debe ser true, false, 1 o 0.")
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def trim_database_url(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        is_production = self.APP_ENV.casefold() in {"production", "prod", "preview"} or (
            (os.getenv("VERCEL_ENV") or "").casefold() in {"production", "preview"}
        )
        if is_production:
            if self.SECRET_KEY == "change-me-before-production" or len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY debe ser un secreto privado de al menos 32 caracteres en producción.")
            if not self.COOKIE_SECURE:
                raise ValueError("COOKIE_SECURE debe estar activado en producción.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
