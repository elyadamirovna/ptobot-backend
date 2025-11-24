"""Application configuration."""

from __future__ import annotations

from pydantic import AliasChoices, BaseSettings, Field
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables."""

    app_title: str = Field("Ptobot backend", description="Application title")
    yc_s3_endpoint: str = Field(
        "https://storage.yandexcloud.net", description="Yandex Cloud S3 endpoint"
    )
    yc_s3_region: str = Field("ru-central1", description="Yandex Cloud region")
    yc_s3_bucket: str = Field(
        "ptobot-assets",
        description="Bucket used for storing uploaded report assets",
        validation_alias=AliasChoices("YC_S3_BUCKET", "YANDEX_BUCKET"),
    )
    yc_s3_access_key_id: str | None = Field(
        None,
        description="Yandex Cloud access key id",
        validation_alias=AliasChoices("YC_S3_ACCESS_KEY_ID"),
    )
    yc_s3_secret_access_key: str | None = Field(
        None,
        description="Yandex Cloud secret access key",
        validation_alias=AliasChoices("YC_S3_SECRET_ACCESS_KEY"),
    )
    bot_token: str | None = Field(None, description="Telegram bot token")
    max_reports: int = Field(500, description="Maximum number of stored reports")

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False, extra="ignore")


settings = Settings()
