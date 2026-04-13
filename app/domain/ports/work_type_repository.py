"""Port definition for work type persistence."""
from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from app.domain.entities.work_type import WorkType


@runtime_checkable
class WorkTypeRepository(Protocol):
    async def list(self) -> Iterable[WorkType]:
        ...

    async def get_by_id(self, work_type_id: str) -> WorkType | None:
        ...

    async def create(self, work_type: WorkType) -> WorkType:
        ...

    async def update(self, work_type: WorkType) -> WorkType | None:
        ...

    async def delete(self, work_type_id: str) -> bool:
        ...
