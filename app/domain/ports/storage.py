"""Port for uploading files to a storage backend."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from fastapi import UploadFile


@runtime_checkable
class StoragePort(Protocol):
    async def upload(self, file: UploadFile) -> str:
        ...
