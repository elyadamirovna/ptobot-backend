"""Application configuration management."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional


class Settings:
    """Container for application settings sourced from environment variables."""

    app_title: str = "Ptobot backend"
    cors_allow_origins: List[str] = ["*"]

    yc_s3_endpoint: str = os.getenv("YC_S3_ENDPOINT", "https://storage.yandexcloud.net")
    yc_s3_region: str = os.getenv("YC_S3_REGION", "ru-central1")
    yc_s3_bucket: str = os.getenv("YC_S3_BUCKET") or os.getenv("YANDEX_BUCKET", "ptobot-assets")
    yc_s3_access_key_id: Optional[str] = os.getenv("YC_S3_ACCESS_KEY_ID")
    yc_s3_secret_access_key: Optional[str] = os.getenv("YC_S3_SECRET_ACCESS_KEY")

    bot_token: Optional[str] = os.getenv("BOT_TOKEN")
    webapp_url: str = os.getenv("WEBAPP_URL", "https://reports-frontend.onrender.com")

    reports_limit: int = int(os.getenv("REPORTS_LIMIT", 500))


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()
