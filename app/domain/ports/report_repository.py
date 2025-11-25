"""Port definition for report persistence."""
from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from app.domain.entities.report import Report


@runtime_checkable
class ReportRepository(Protocol):
    async def add(self, report: Report) -> Report:
        ...

    async def list(self, *, user_id: str | None = None, work_type_id: str | None = None) -> Iterable[Report]:
        ...

    async def next_id(self) -> str:
        ...
