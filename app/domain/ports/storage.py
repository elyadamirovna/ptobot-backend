"""Port for uploading files to a storage backend."""
from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from fastapi import UploadFile


@runtime_checkable
class StoragePort(Protocol):
    async def upload(
        self,
        file: UploadFile,
        *,
        site_id: str,
        site_name: str | None,
        report_id: str,
        report_date: date,
    ) -> str:
        ...

    async def delete(self, url: str) -> None:
        ...
