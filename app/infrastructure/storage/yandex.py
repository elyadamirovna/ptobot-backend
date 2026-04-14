"""Yandex Object Storage adapter with async-friendly uploads."""
from __future__ import annotations

import asyncio
import logging
import re
import uuid
from datetime import date
from pathlib import Path
from time import perf_counter

import boto3
from botocore.config import Config
from fastapi import UploadFile

from app.config import Settings
from app.domain.ports import StoragePort

logger = logging.getLogger(__name__)

CYRILLIC_TO_LATIN = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def slugify_site_name(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return ""

    transliterated = "".join(CYRILLIC_TO_LATIN.get(char, char) for char in raw)
    slug = re.sub(r"[^a-z0-9]+", "-", transliterated).strip("-")
    return re.sub(r"-{2,}", "-", slug)


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

    async def upload(
        self,
        file: UploadFile,
        *,
        site_id: str,
        site_name: str | None,
        report_id: str,
        report_date: date,
    ) -> str:
        total_started_at = perf_counter()
        ext = Path(file.filename or "").suffix or ".jpg"
        site_slug = slugify_site_name(site_name)
        site_prefix = f"{site_id}-{site_slug}" if site_slug else site_id
        original_name = Path(file.filename or "").stem.strip()
        file_slug = slugify_site_name(original_name) or "photo"
        key = str(
            self._settings.storage_key_prefix()
            / site_prefix
            / f"{report_date:%Y}"
            / f"{report_date:%m}"
            / f"{report_date:%d}"
            / report_id
            / f"{uuid.uuid4().hex}-{file_slug}{ext.lower()}"
        )
        read_started_at = perf_counter()
        content = await file.read()
        read_elapsed = perf_counter() - read_started_at
        upload_started_at = perf_counter()

        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._settings.yc_s3_bucket,
            Key=key,
            Body=content,
            ContentType=file.content_type,
            ACL="public-read",
        )

        upload_elapsed = perf_counter() - upload_started_at
        total_elapsed = perf_counter() - total_started_at

        logger.info(
            "Uploaded photo '%s' (%d bytes) to key '%s' in %.3fs "
            "(read %.3fs, s3 %.3fs)",
            file.filename or key,
            len(content),
            key,
            total_elapsed,
            read_elapsed,
            upload_elapsed,
        )

        return f"https://{self._settings.yc_s3_bucket}.storage.yandexcloud.net/{key}"

    async def delete(self, url: str) -> None:
        bucket_prefix = f"https://{self._settings.yc_s3_bucket}.storage.yandexcloud.net/"
        if not url.startswith(bucket_prefix):
            logger.warning("Skip deleting unsupported storage url '%s'", url)
            return

        key = url.removeprefix(bucket_prefix)
        if not key:
            return

        await asyncio.to_thread(
            self._client.delete_object,
            Bucket=self._settings.yc_s3_bucket,
            Key=key,
        )
