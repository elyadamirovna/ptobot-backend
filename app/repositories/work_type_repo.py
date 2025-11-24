"""In-memory repository for work types."""

from __future__ import annotations

from typing import List

from app.models.work_type import WorkTypeOut
from app.repositories.base import WorkTypeRepositoryProtocol


class WorkTypeRepository(WorkTypeRepositoryProtocol):
    """Provides access to available work types."""

    def __init__(self) -> None:
        self._work_types: List[WorkTypeOut] = [
            WorkTypeOut(id=1, name="Земляные работы"),
            WorkTypeOut(id=2, name="Бетонирование"),
            WorkTypeOut(id=3, name="Монтаж конструкций"),
        ]

    def list_work_types(self) -> List[WorkTypeOut]:
        return list(self._work_types)
