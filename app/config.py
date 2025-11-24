"""Application configuration and shared constants."""

from __future__ import annotations

import logging
import os
from typing import Any

import boto3

logger = logging.getLogger(__name__)

# Application constants
MAX_REPORTS = 500
BOT_TASK_ATTR = "bot_task"

# Yandex Object Storage configuration
YC_S3_ENDPOINT = os.getenv("YC_S3_ENDPOINT", "https://storage.yandexcloud.net")
YC_S3_REGION = os.getenv("YC_S3_REGION", "ru-central1")
# Prefer YC_S3_BUCKET but allow legacy YANDEX_BUCKET for easier configuration.
YC_S3_BUCKET = os.getenv("YC_S3_BUCKET") or os.getenv("YANDEX_BUCKET", "ptobot-assets")

YC_S3_ACCESS_KEY_ID = os.getenv("YC_S3_ACCESS_KEY_ID")
YC_S3_SECRET_ACCESS_KEY = os.getenv("YC_S3_SECRET_ACCESS_KEY")


def create_s3_client() -> Any:
    """Create a configured boto3 S3 client."""

    return boto3.client(
        "s3",
        endpoint_url=YC_S3_ENDPOINT,
        region_name=YC_S3_REGION,
        aws_access_key_id=YC_S3_ACCESS_KEY_ID,
        aws_secret_access_key=YC_S3_SECRET_ACCESS_KEY,
    )
