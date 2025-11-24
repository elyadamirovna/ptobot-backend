"""Business logic for reports management."""

from __future__ import annotations

import datetime as dt
from typing import List, Optional

from fastapi import UploadFile

from app.models.report import ReportOut
from app.repositories.report_repo import ReportRepository
from app.services.storage_service import StorageService


class ReportService:
    """Handles creation and retrieval of reports."""

    def __init__(self, repository: ReportRepository, storage_service: StorageService) -> None:
        self._repository = repository
        self._storage_service = storage_service

    async def create_report(
        self,
        *,
        user_id: str,
        work_type_id: str,
        description: str,
        people: str,
        volume: str,
        machines: str,
        photos: List[UploadFile],
    ) -> ReportOut:
        photo_urls: List[str] = []
        for photo in photos:
            url = await self._storage_service.upload_to_yandex(photo)
            photo_urls.append(url)

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

        self._repository.add_report(report)
        return report

    def list_reports(self, *, user_id: Optional[str] = None, work_type_id: Optional[str] = None) -> List[ReportOut]:
        return self._repository.list_reports(user_id=user_id, work_type_id=work_type_id)
