"""File storage service."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from app.core.config import Settings


class StorageService:
    """Handle uploading files to Yandex Object Storage."""

    def __init__(self, s3_client: Any, settings: Settings) -> None:
        self._s3_client = s3_client
        self._settings = settings

    async def upload(self, file: UploadFile) -> str:
        """Upload a file to S3 and return its public URL."""

        ext = Path(file.filename or "").suffix or ".jpg"
        key = f"reports/{uuid.uuid4().hex}{ext}"
        content = await file.read()

        self._s3_client.put_object(
            Bucket=self._settings.yc_s3_bucket,
            Key=key,
            Body=content,
            ContentType=file.content_type,
            ACL="public-read",
        )

        return (
            f"https://{self._settings.yc_s3_bucket}.storage.yandexcloud.net/{key}"
        )
