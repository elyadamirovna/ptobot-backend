"""Application service for report-related use cases."""
from __future__ import annotations

from typing import Iterable, List, Sequence

from fastapi import UploadFile

from app.application.dto import ReportCreateCommand
from app.domain.entities.report import Report
from app.domain.ports import Clock, ReportRepository, StoragePort


class ReportService:
    """Coordinates report creation and retrieval via defined ports."""

    def __init__(self, *, repository: ReportRepository, storage: StoragePort, clock: Clock) -> None:
        self._repository = repository
        self._storage = storage
        self._clock = clock

    async def create_report(self, payload: ReportCreateCommand, photos: Sequence[UploadFile]) -> Report:
        photo_urls: List[str] = []
        for photo in photos:
            photo_urls.append(await self._storage.upload(photo))

        report_id = await self._repository.next_id()
        created_at = self._clock.now()

        report = Report(
            id=report_id,
            user_id=payload.user_id,
            work_type_id=payload.work_type_id,
            description=payload.description,
            people=payload.people,
            volume=payload.volume,
            machines=payload.machines,
            created_at=created_at,
            photo_urls=photo_urls,
        )
        await self._repository.add(report)
        return report

    async def list_reports(self, *, user_id: str | None, work_type_id: str | None) -> Iterable[Report]:
        return await self._repository.list(user_id=user_id, work_type_id=work_type_id)
