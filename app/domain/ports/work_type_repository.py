"""Port definition for work type persistence."""
from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from app.domain.entities.work_type import WorkType


@runtime_checkable
class WorkTypeRepository(Protocol):
    async def list(self) -> Iterable[WorkType]:
        ...
