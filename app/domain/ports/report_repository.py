"""Port definition for report persistence."""
from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from app.domain.entities import Report, ReportHistoryItem


@runtime_checkable
class ReportRepository(Protocol):
    async def add(self, report: Report) -> Report:
        ...

    async def list(
        self,
        *,
        site_id: str | None = None,
        user_id: str | None = None,
        work_type_id: str | None = None,
    ) -> Iterable[Report]:
        ...

    async def list_history_by_site(
        self,
        *,
        site_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
        work_type_id: str | None = None,
        limit: int | None = None,
    ) -> Iterable[ReportHistoryItem]:
        ...

    async def next_id(self) -> str:
        ...
