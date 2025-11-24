"""Repository for available work types."""

from __future__ import annotations

from typing import List

from app.models.schemas import WorkTypeOut


class WorkTypeRepository:
    """Provides access to supported work types."""

    def get_all(self) -> List[WorkTypeOut]:
        return [
            WorkTypeOut(id=1, name="Земляные работы"),
            WorkTypeOut(id=2, name="Бетонирование"),
            WorkTypeOut(id=3, name="Монтаж конструкций"),
        ]
