"""Yandex Object Storage adapter with async-friendly uploads."""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import boto3
from botocore.config import Config
from fastapi import UploadFile

from app.config import Settings
from app.domain.ports import StoragePort


class YandexStorage(StoragePort):
    def __init__(self, settings: Settings) -> None:
        if not settings.has_storage_credentials:
            raise ValueError("YC_S3_ACCESS_KEY_ID and YC_S3_SECRET_ACCESS_KEY must be provided for uploads")

        self._settings = settings
        self._client = boto3.client(
            "s3",
            endpoint_url=str(settings.yc_s3_endpoint),
            region_name=settings.yc_s3_region,
            aws_access_key_id=settings.yc_s3_access_key_id,
            aws_secret_access_key=settings.yc_s3_secret_access_key,
            config=Config(retries={"max_attempts": 3, "mode": "standard"}, connect_timeout=5, read_timeout=30),
        )

    async def upload(self, file: UploadFile) -> str:
        ext = Path(file.filename or "").suffix or ".jpg"
        key = str(self._settings.storage_key_prefix() / f"{uuid.uuid4().hex}{ext}")
        content = await file.read()

        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._settings.yc_s3_bucket,
            Key=key,
            Body=content,
            ContentType=file.content_type,
            ACL="public-read",
        )

        return f"https://{self._settings.yc_s3_bucket}.storage.yandexcloud.net/{key}"
