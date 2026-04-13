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

    async def get_by_id(self, work_type_id: str) -> WorkType | None:
        model = self._session.get(WorkTypeModel, work_type_id)
        if model is None:
            return None
        return self._to_entity(model)

    async def create(self, work_type: WorkType) -> WorkType:
        model = WorkTypeModel(id=work_type.id, name=work_type.name)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, work_type: WorkType) -> WorkType | None:
        model = self._session.get(WorkTypeModel, work_type.id)
        if model is None:
            return None

        model.name = work_type.name
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, work_type_id: str) -> bool:
        model = self._session.get(WorkTypeModel, work_type_id)
        if model is None:
            return False

        self._session.delete(model)
        self._session.commit()
        return True

    def _bootstrap_defaults(self) -> None:
        existing = {item.id for item in self._session.execute(select(WorkTypeModel)).scalars().all()}
        for identifier, name in DEFAULT_WORK_TYPES:
            if identifier not in existing:
                self._session.merge(WorkTypeModel(id=identifier, name=name))
        self._session.commit()

    @staticmethod
    def _to_entity(model: WorkTypeModel) -> WorkType:
        return WorkType(id=model.id, name=model.name)
