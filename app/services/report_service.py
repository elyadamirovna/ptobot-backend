"""Application service for report management."""

from __future__ import annotations

import datetime as dt
from typing import List, Optional

from fastapi import UploadFile

from app.models.schemas import ReportOut
from app.repositories.report_repository import ReportRepository
from app.services.storage_service import StorageService


class ReportService:
    """Coordinates report persistence and file uploads."""

    def __init__(self, repository: ReportRepository, storage: StorageService):
        self._repository = repository
        self._storage = storage

    async def create_report(
        self,
        user_id: str,
        work_type_id: str,
        description: str,
        people: str,
        volume: str,
        machines: str,
        photos: List[UploadFile],
    ) -> ReportOut:
        photo_urls = [await self._storage.upload(photo) for photo in photos]
        report_id = self._repository.next_id()
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()

        report = ReportOut(
            id=report_id,
            user_id=user_id,
            work_type_id=str(work_type_id),
            description=description,
            people=people,
            volume=volume,
            machines=machines,
            created_at=created_at,
            photo_urls=photo_urls,
        )

        return self._repository.save(report)

    def list_reports(
        self, user_id: Optional[str] = None, work_type_id: Optional[str] = None
    ) -> List[ReportOut]:
        return self._repository.list(user_id=user_id, work_type_id=work_type_id)
