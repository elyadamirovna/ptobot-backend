"""SQLAlchemy-based repository for work types."""
from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import WorkType
from app.domain.ports import WorkTypeRepository
from app.infrastructure.work_types.models import WorkTypeModel


DEFAULT_WORK_TYPES: list[tuple[str, str]] = [
    ("1", "Земляные работы"),
    ("2", "Бетонирование"),
    ("3", "Монтаж конструкций"),
]


class SqlAlchemyWorkTypeRepository(WorkTypeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    async def list(self) -> Iterable[WorkType]:
        work_types = self._session.execute(select(WorkTypeModel)).scalars().all()
        if not work_types:
            self._bootstrap_defaults()
            work_types = self._session.execute(select(WorkTypeModel)).scalars().all()

        return [self._to_entity(model) for model in work_types]

    def _bootstrap_defaults(self) -> None:
        existing = {item.id for item in self._session.execute(select(WorkTypeModel)).scalars().all()}
        for identifier, name in DEFAULT_WORK_TYPES:
            if identifier not in existing:
                self._session.merge(WorkTypeModel(id=identifier, name=name))
        self._session.commit()

    @staticmethod
    def _to_entity(model: WorkTypeModel) -> WorkType:
        return WorkType(id=model.id, name=model.name)
