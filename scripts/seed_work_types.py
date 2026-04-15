"""Seed default work types into the database."""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from app.infrastructure.database import SessionLocal
from app.infrastructure.work_types.models import WorkTypeModel

DEFAULT_WORK_TYPES = [
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


def seed() -> None:
    db = SessionLocal()
    try:
        created = 0
        for item in DEFAULT_WORK_TYPES:
            work_type_id = item["id"]
            row = db.query(WorkTypeModel).filter(WorkTypeModel.id == work_type_id).first()
            if row is None:
                db.add(
                    WorkTypeModel(
                        id=work_type_id,
                        name=item["name"],
                        parent_id=item["parent_id"],
                        sort_order=item["sort_order"],
                        unit=item["unit"],
                        is_active=item["is_active"],
                        requires_volume=item["requires_volume"],
                        requires_people=item["requires_people"],
                        requires_machines=item["requires_machines"],
                    )
                )
                created += 1
                print(f"  added {work_type_id} -> {item['name']}")
            else:
                row.name = item["name"]
                row.parent_id = item["parent_id"]
                row.sort_order = item["sort_order"]
                row.unit = item["unit"]
                row.is_active = item["is_active"]
                row.requires_volume = item["requires_volume"]
                row.requires_people = item["requires_people"]
                row.requires_machines = item["requires_machines"]
                print(f"  sync  {work_type_id} -> {item['name']}")

        db.commit()
        print(f"\nDone. {created} work type(s) created.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
