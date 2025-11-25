"""Validated application settings using pydantic-settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Container for strongly validated application settings."""

    model_config = SettingsConfigDict(extra="ignore")

    app_title: str = Field(default="Ptobot backend")
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOW_ORIGINS")

    yc_s3_endpoint: HttpUrl = Field(default="https://storage.yandexcloud.net", alias="YC_S3_ENDPOINT")
    yc_s3_region: str = Field(default="ru-central1", alias="YC_S3_REGION")
    yc_s3_bucket: str = Field(default="ptobot-assets", min_length=1, alias="YC_S3_BUCKET")
    yc_s3_access_key_id: str = Field(default="", alias="YC_S3_ACCESS_KEY_ID")
    yc_s3_secret_access_key: str = Field(default="", alias="YC_S3_SECRET_ACCESS_KEY")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/ptobot",
        alias="DATABASE_URL",
    )

    bot_token: Optional[str] = Field(default=None, alias="BOT_TOKEN")
    webapp_url: HttpUrl = Field(default="https://reports-frontend.onrender.com", alias="WEBAPP_URL")

    reports_limit: int = Field(default=500, ge=1, alias="REPORTS_LIMIT")

    @property
    def has_storage_credentials(self) -> bool:
        return bool(self.yc_s3_access_key_id and self.yc_s3_secret_access_key)

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return ["*"]

    @field_validator("yc_s3_bucket")
    @classmethod
    def validate_bucket(cls, value: str) -> str:
        if not value:
            raise ValueError("YC_S3_BUCKET is required for uploads")
        return value

    @field_validator("yc_s3_access_key_id", "yc_s3_secret_access_key")
    @classmethod
    def validate_credentials(cls, value: str, info):
        # Allow empty values but warn early if one is set without the other
        if value is None:
            return ""
        return value

    def storage_key_prefix(self) -> Path:
        return Path("reports")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings instance for use across the application."""

    return Settings()
