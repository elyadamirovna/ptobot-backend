"""File storage service for Yandex Cloud."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.infrastructure.yandex_s3 import get_s3_client


class StorageService:
    """Uploads files to Yandex Object Storage."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = get_s3_client(settings)

    async def upload_to_yandex(self, file: UploadFile) -> str:
        """Upload a file and return its public URL."""

        ext = Path(file.filename or "").suffix or ".jpg"
        key = f"reports/{uuid.uuid4().hex}{ext}"

        content = await file.read()

        self._client.put_object(
            Bucket=self._settings.yc_s3_bucket,
            Key=key,
            Body=content,
            ContentType=file.content_type,
            ACL="public-read",
        )

        return f"https://{self._settings.yc_s3_bucket}.storage.yandexcloud.net/{key}"
