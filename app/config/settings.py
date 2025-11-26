# settings.py

from __future__ import annotations
from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Iterable, List, Optional

from pydantic import Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, EnvSettingsSource, SettingsConfigDict


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

    @staticmethod
    def _normalize_origins(value: str | Iterable[str] | None) -> List[str]:
        if value is None:
            return DEFAULT_CORS_ORIGINS.copy()

        if isinstance(value, str):
            parts = re.split(r"[\s,]+", value)
        else:
            parts = list(value)

        filtered = [item for item in (str(part).strip() for part in parts) if item]
        return filtered or DEFAULT_CORS_ORIGINS.copy()

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | List[str]) -> List[str]:
        return cls._normalize_origins(value)

    @model_validator(mode="after")
    def ensure_origins_list(self) -> "Settings":
        self.cors_allow_origins = self._normalize_origins(self.cors_allow_origins)
        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type["Settings"],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        class LenientEnvSettingsSource(EnvSettingsSource):
            def decode_complex_value(self, field_name, field, value):
                try:
                    return super().decode_complex_value(field_name, field, value)
                except (json.JSONDecodeError, ValueError):
                    return value

        return (
            init_settings,
            dotenv_settings,
            LenientEnvSettingsSource(settings_cls),
            file_secret_settings,
        )

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
    assert isinstance(settings.cors_allow_origins, list)
    logger.info(
        "CORS_ALLOW_ORIGINS parsed as list with %d entries: %s",
        len(settings.cors_allow_origins),
        settings.cors_allow_origins,
    )
    return settings


# ⬇️ Убедись, что ты экспортируешь нужные объекты
__all__ = ["Settings", "get_settings"]
