"""SQLAlchemy-based repository for work types."""
from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import WorkType
from app.domain.ports import WorkTypeRepository
from app.infrastructure.work_types.models import WorkTypeModel


DEFAULT_WORK_TYPES: list[dict[str, object]] = [
    {
        "id": "roadway",
        "name": "Устройство проезжей части",
        "parent_id": None,
        "sort_order": 10,
        "unit": None,
        "is_active": True,
        "requires_volume": False,
        "requires_people": False,
        "requires_machines": False,
    },
    {
        "id": "roadway-subgrade",
        "name": "Разработка корыта",
        "parent_id": "roadway",
        "sort_order": 11,
        "unit": "м3",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": True,
    },
    {
        "id": "roadway-sand-base",
        "name": "Устройство песчаного основания",
        "parent_id": "roadway",
        "sort_order": 12,
        "unit": "м2",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": True,
    },
    {
        "id": "roadway-crushed-base",
        "name": "Устройство щебеночного основания",
        "parent_id": "roadway",
        "sort_order": 13,
        "unit": "м2",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": True,
    },
    {
        "id": "roadway-lower-asphalt",
        "name": "Устройство нижнего слоя покрытия",
        "parent_id": "roadway",
        "sort_order": 15,
        "unit": "м2",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": True,
    },
    {
        "id": "roadway-upper-asphalt",
        "name": "Устройство верхнего слоя покрытия",
        "parent_id": "roadway",
        "sort_order": 16,
        "unit": "м2",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": True,
    },
    {
        "id": "sidewalk",
        "name": "Устройство тротуара",
        "parent_id": None,
        "sort_order": 20,
        "unit": None,
        "is_active": True,
        "requires_volume": False,
        "requires_people": False,
        "requires_machines": False,
    },
    {
        "id": "sidewalk-sand-base",
        "name": "Устройство песчаного основания",
        "parent_id": "sidewalk",
        "sort_order": 22,
        "unit": "м2",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": True,
    },
    {
        "id": "sidewalk-paving-slabs",
        "name": "Укладка тротуарной плитки",
        "parent_id": "sidewalk",
        "sort_order": 25,
        "unit": "м2",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": False,
    },
    {
        "id": "curbstone",
        "name": "Устройство бортового камня (бетонный)",
        "parent_id": None,
        "sort_order": 30,
        "unit": None,
        "is_active": True,
        "requires_volume": False,
        "requires_people": False,
        "requires_machines": False,
    },
    {
        "id": "curbstone-install",
        "name": "Установка бортового камня",
        "parent_id": "curbstone",
        "sort_order": 34,
        "unit": "п.м.",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": True,
    },
    {
        "id": "lawn",
        "name": "Устройство газона",
        "parent_id": None,
        "sort_order": 40,
        "unit": None,
        "is_active": True,
        "requires_volume": False,
        "requires_people": False,
        "requires_machines": False,
    },
    {
        "id": "lawn-seeding",
        "name": "Посев газона",
        "parent_id": "lawn",
        "sort_order": 45,
        "unit": "м2",
        "is_active": True,
        "requires_volume": True,
        "requires_people": True,
        "requires_machines": False,
    },
]


class SqlAlchemyWorkTypeRepository(WorkTypeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    async def list(self) -> Iterable[WorkType]:
        work_types = self._session.execute(
            select(WorkTypeModel).order_by(WorkTypeModel.sort_order.asc(), WorkTypeModel.name.asc())
        ).scalars().all()
        if not work_types:
            self._bootstrap_defaults()
            work_types = self._session.execute(
                select(WorkTypeModel).order_by(WorkTypeModel.sort_order.asc(), WorkTypeModel.name.asc())
            ).scalars().all()

        return [self._to_entity(model) for model in work_types]

    async def get_by_id(self, work_type_id: str) -> WorkType | None:
        model = self._session.get(WorkTypeModel, work_type_id)
        if model is None:
            return None
        return self._to_entity(model)

    async def create(self, work_type: WorkType) -> WorkType:
        model = WorkTypeModel(
            id=work_type.id,
            name=work_type.name,
            parent_id=work_type.parent_id,
            sort_order=work_type.sort_order,
            unit=work_type.unit,
            is_active=work_type.is_active,
            requires_volume=work_type.requires_volume,
            requires_people=work_type.requires_people,
            requires_machines=work_type.requires_machines,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, work_type: WorkType) -> WorkType | None:
        model = self._session.get(WorkTypeModel, work_type.id)
        if model is None:
            return None

        model.name = work_type.name
        model.parent_id = work_type.parent_id
        model.sort_order = work_type.sort_order
        model.unit = work_type.unit
        model.is_active = work_type.is_active
        model.requires_volume = work_type.requires_volume
        model.requires_people = work_type.requires_people
        model.requires_machines = work_type.requires_machines
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
        for item in DEFAULT_WORK_TYPES:
            if item["id"] not in existing:
                self._session.merge(
                    WorkTypeModel(
                        id=str(item["id"]),
                        name=str(item["name"]),
                        parent_id=item["parent_id"],
                        sort_order=int(item["sort_order"]),
                        unit=item["unit"],
                        is_active=bool(item["is_active"]),
                        requires_volume=bool(item["requires_volume"]),
                        requires_people=bool(item["requires_people"]),
                        requires_machines=bool(item["requires_machines"]),
                    )
                )
        self._session.commit()

    @staticmethod
    def _to_entity(model: WorkTypeModel) -> WorkType:
        return WorkType(
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            sort_order=model.sort_order,
            unit=model.unit,
            is_active=model.is_active,
            requires_volume=model.requires_volume,
            requires_people=model.requires_people,
            requires_machines=model.requires_machines,
        )
