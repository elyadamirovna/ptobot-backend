"""Business logic for reports."""

from __future__ import annotations

import datetime as dt
from typing import Iterable, List, Optional

from fastapi import UploadFile

from app.models.report import Report
from app.repositories.report_repo import ReportRepository
from app.services.storage_service import StorageService


class ReportService:
    """Отвечает за создание и получение отчётов."""

    def __init__(self, repo: ReportRepository, storage: StorageService) -> None:
        self._repo = repo
        self._storage = storage

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
    ) -> Report:
        photo_urls: List[str] = []
        for photo in photos:
            url = await self._storage.upload(photo)
            photo_urls.append(url)

        report = Report(
            id=self._repo.next_id(),
            user_id=user_id,
            work_type_id=str(work_type_id),
            description=description,
            people=people,
            volume=volume,
            machines=machines,
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            photo_urls=photo_urls,
        )

        self._repo.add(report)
        return report

    def list_reports(
        self, *, user_id: Optional[str] = None, work_type_id: Optional[str] = None
    ) -> Iterable[Report]:
        reports = self._repo.list()
        if user_id is not None:
            reports = [r for r in reports if r.user_id == user_id]
        if work_type_id is not None:
            reports = [r for r in reports if r.work_type_id == work_type_id]
        return reports
