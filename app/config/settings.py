# settings.py

from __future__ import annotations
from functools import lru_cache
import re
from pathlib import Path
from typing import List, Optional

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_CORS_ORIGINS = [
    "https://ptobot-frontend.onrender.com",
    "https://tgapp-web.telegram.org",
    "https://web.telegram.org",
]


class Settings(BaseSettings):
    """Container for strongly validated application settings."""

    model_config = SettingsConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="ignore",
    )

    app_title: str = Field(default="Ptobot backend")
    cors_allow_origins: List[str] = Field(
        default_factory=lambda: DEFAULT_CORS_ORIGINS.copy(),
        alias="CORS_ALLOW_ORIGINS"
    )

    yc_s3_endpoint: HttpUrl = Field(default="https://storage.yandexcloud.net", alias="YC_S3_ENDPOINT")
    yc_s3_region: str = Field(default="ru-central1", alias="YC_S3_REGION")
    yc_s3_bucket: str = Field(default="ptobot-assets", min_length=1, alias="YC_S3_BUCKET")
    yc_s3_access_key_id: str = Field(default="", alias="YC_S3_ACCESS_KEY_ID")
    yc_s3_secret_access_key: str = Field(default="", alias="YC_S3_SECRET_ACCESS_KEY")

    database_url: str = Field(alias="DATABASE_URL")
    bot_token: Optional[str] = Field(default=None, alias="BOT_TOKEN")
    webapp_url: HttpUrl = Field(default="https://reports-frontend.onrender.com", alias="WEBAPP_URL")
    webhook_path: str = Field(default="/bot", alias="WEBHOOK_PATH")
    webhook_secret_token: Optional[str] = Field(default=None, alias="WEBHOOK_SECRET_TOKEN")

    reports_limit: int = Field(default=500, ge=1, alias="REPORTS_LIMIT")

    @property
    def has_storage_credentials(self) -> bool:
        return bool(self.yc_s3_access_key_id and self.yc_s3_secret_access_key)

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | List[str]) -> List[str]:
        if value is None:
            return DEFAULT_CORS_ORIGINS.copy()
        if isinstance(value, list):
            return value or DEFAULT_CORS_ORIGINS.copy()
        if isinstance(value, str):
            parts = re.split(r"[\s,]+", value)
            filtered = [item for item in (part.strip() for part in parts) if item]
            return filtered or DEFAULT_CORS_ORIGINS.copy()
        return DEFAULT_CORS_ORIGINS.copy()

    @field_validator("yc_s3_bucket")
    @classmethod
    def validate_bucket(cls, value: str) -> str:
        if not value:
            raise ValueError("YC_S3_BUCKET is required for uploads")
        return value

    @field_validator("yc_s3_access_key_id", "yc_s3_secret_access_key")
    @classmethod
    def validate_credentials(cls, value: str, info):
        if value is None:
            return ""
        return value

    @field_validator("webhook_path")
    @classmethod
    def ensure_webhook_path(cls, value: str) -> str:
        value = value or "/bot"
        return value if value.startswith("/") else f"/{value}"

    def storage_key_prefix(self) -> Path:
        return Path("reports")


# ⬇️ Теперь функция get_settings вне класса
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"CORS_ALLOW_ORIGINS parsed as: {settings.cors_allow_origins}")
    return settings


# ⬇️ Убедись, что ты экспортируешь нужные объекты
__all__ = ["Settings", "get_settings"]
