"""Service for interacting with object storage."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import UploadFile


class StorageService:
    """Uploads files to the configured storage bucket."""

    def __init__(self, client: Any, bucket: str):
        self._client = client
        self._bucket = bucket

    async def upload(self, file: UploadFile) -> str:
        ext = Path(file.filename or "").suffix or ".jpg"
        key = f"reports/{uuid.uuid4().hex}{ext}"
        content = await file.read()

        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=content,
            ContentType=file.content_type,
            ACL="public-read",
        )

        return f"https://{self._bucket}.storage.yandexcloud.net/{key}"
