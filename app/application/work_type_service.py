"""Application service for work types."""
from __future__ import annotations

from typing import Iterable

from app.domain.entities.work_type import WorkType
from app.domain.ports import WorkTypeRepository


class WorkTypeService:
    def __init__(self, repository: WorkTypeRepository) -> None:
        self._repository = repository

    async def list_work_types(self) -> Iterable[WorkType]:
        return await self._repository.list()
