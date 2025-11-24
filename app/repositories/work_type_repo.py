"""In-memory repository for work types."""

from __future__ import annotations

from typing import Iterable, List

from app.models.work_type import WorkType
from app.repositories.base import WorkTypeRepositoryBase


class WorkTypeRepository(WorkTypeRepositoryBase):
    """Хранит заранее заданные виды работ."""

    def __init__(self) -> None:
        self._work_types: List[WorkType] = [
            WorkType(id=1, name="Земляные работы"),
            WorkType(id=2, name="Бетонирование"),
            WorkType(id=3, name="Монтаж конструкций"),
        ]

    def list(self) -> Iterable[WorkType]:
        return list(self._work_types)
