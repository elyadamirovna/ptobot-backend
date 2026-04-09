"""Application service for fetching history of reports for a site."""
from __future__ import annotations

from datetime import date
from typing import Iterable

from fastapi import HTTPException, status

from app.domain.entities import ReportHistoryItem, User
from app.domain.ports import ReportRepository
from app.application.site_service import SiteService


class ReportHistoryService:
    def __init__(self, repository: ReportRepository, site_service: SiteService) -> None:
        self._repository = repository
        self._site_service = site_service

    async def get_site_report_history(
        self,
        *,
        user: User,
        site_id: str,
        date_from: date | None = None,
        date_to: date | None = None,
        work_type_id: str | None = None,
        limit: int | None = None,
    ) -> Iterable[ReportHistoryItem]:
        self._site_service.get_site_for_user(site_id=site_id, user=user)

        if date_from and date_to and date_from > date_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Дата начала не может быть позже даты окончания",
            )

        return await self._repository.list_history_by_site(
            site_id=site_id,
            date_from=date_from.isoformat() if date_from else None,
            date_to=date_to.isoformat() if date_to else None,
            work_type_id=work_type_id,
            limit=limit,
        )
