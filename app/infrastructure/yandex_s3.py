"""Low-level Yandex Object Storage client factory."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import boto3

from app.core.config import Settings


@lru_cache
def get_s3_client(settings: Settings) -> Any:
    """Create a boto3 S3 client configured for Yandex Cloud."""

    return boto3.client(
        "s3",
        endpoint_url=settings.yc_s3_endpoint,
        region_name=settings.yc_s3_region,
        aws_access_key_id=settings.yc_s3_access_key_id,
        aws_secret_access_key=settings.yc_s3_secret_access_key,
    )
