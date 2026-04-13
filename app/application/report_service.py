"""Application service for report-related use cases."""
from __future__ import annotations

import asyncio
import logging
from time import perf_counter
from typing import Iterable, List, Sequence

from fastapi import UploadFile
from fastapi import HTTPException, status

from app.application.dto import ReportCreateCommand
from app.domain.entities import User
from app.domain.entities.report import Report
from app.application.site_service import SiteService
from app.domain.ports import Clock, ReportRepository, StoragePort

logger = logging.getLogger(__name__)


class ReportService:
    """Coordinates report creation and retrieval via defined ports."""

    def __init__(
        self,
        *,
        repository: ReportRepository,
        storage: StoragePort,
        clock: Clock,
        site_service: SiteService,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._clock = clock
        self._site_service = site_service

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

    async def update_report(
        self,
        *,
        report_id: str,
        user: User,
        work_type_id: str,
        report_date,
        description: str,
        people: str,
        volume: str,
        machines: str,
        keep_photo_urls: Sequence[str],
        new_photos: Sequence[UploadFile],
    ) -> Report:
        existing = await self._repository.get_by_id(report_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отчёт не найден")

        site = self._site_service.get_site_for_user(site_id=existing.site_id, user=user)
        if user.role not in {"admin", "pto_engineer"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Редактирование отчётов доступно только администратору и инженеру ПТО",
            )
        if user.role == "pto_engineer" and site.pto_engineer_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к редактированию этого отчёта",
            )

        keep_set = set(keep_photo_urls)
        removed_urls = [url for url in existing.photo_urls if url not in keep_set]
        appended_urls: List[str] = []
        if new_photos:
            appended_urls = list(await asyncio.gather(*(self._storage.upload(photo) for photo in new_photos)))
        for url in removed_urls:
            await self._storage.delete(url)

        updated = Report(
            id=existing.id,
            user_id=existing.user_id,
            site_id=existing.site_id,
            work_type_id=work_type_id,
            report_date=report_date,
            description=description,
            people=people,
            volume=volume,
            machines=machines,
            created_at=existing.created_at,
            photo_urls=[url for url in existing.photo_urls if url in keep_set] + appended_urls,
        )
        return await self._repository.update(updated)

    async def delete_report(self, *, report_id: str, user: User) -> None:
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Удаление отчётов доступно только администратору",
            )

        existing = await self._repository.get_by_id(report_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отчёт не найден")

        for photo_url in existing.photo_urls:
            await self._storage.delete(photo_url)

        deleted = await self._repository.delete(report_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отчёт не найден")
