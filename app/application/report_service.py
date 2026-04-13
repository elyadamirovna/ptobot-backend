"""Application service for report-related use cases."""
from __future__ import annotations

import asyncio
import logging
from time import perf_counter
from typing import Iterable, List, Sequence

from fastapi import UploadFile

from app.application.dto import ReportCreateCommand
from app.domain.entities.report import Report
from app.domain.ports import Clock, ReportRepository, StoragePort

logger = logging.getLogger(__name__)


class ReportService:
    """Coordinates report creation and retrieval via defined ports."""

    def __init__(self, *, repository: ReportRepository, storage: StoragePort, clock: Clock) -> None:
        self._repository = repository
        self._storage = storage
        self._clock = clock

    async def create_report(self, payload: ReportCreateCommand, photos: Sequence[UploadFile]) -> Report:
        started_at = perf_counter()
        photo_urls: List[str] = list(await asyncio.gather(*(self._storage.upload(photo) for photo in photos)))

        report_id = await self._repository.next_id()
        created_at = self._clock.now()

        report = Report(
            id=report_id,
            user_id=payload.user_id,
            site_id=payload.site_id,
            work_type_id=payload.work_type_id,
            report_date=payload.report_date,
            description=payload.description,
            people=payload.people,
            volume=payload.volume,
            machines=payload.machines,
            created_at=created_at,
            photo_urls=photo_urls,
        )
        await self._repository.add(report)
        logger.info(
            "Created report %s with %d photos in %.3fs",
            report.id,
            len(photo_urls),
            perf_counter() - started_at,
        )
        return report

    async def list_reports(
        self,
        *,
        site_id: str | None,
        user_id: str | None,
        work_type_id: str | None,
    ) -> Iterable[Report]:
        return await self._repository.list(site_id=site_id, user_id=user_id, work_type_id=work_type_id)
