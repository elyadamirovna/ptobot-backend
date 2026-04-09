"""Seed default work types into the database."""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from app.infrastructure.database import SessionLocal
from app.infrastructure.work_types.models import WorkTypeModel

DEFAULT_WORK_TYPES = [
    ("1", "Земляные работы"),
    ("2", "Бетонирование"),
    ("3", "Монтаж конструкций"),
]


def seed() -> None:
    db = SessionLocal()
    try:
        created = 0
        for work_type_id, name in DEFAULT_WORK_TYPES:
            row = db.query(WorkTypeModel).filter(WorkTypeModel.id == work_type_id).first()
            if row is None:
                db.add(WorkTypeModel(id=work_type_id, name=name))
                created += 1
                print(f"  added {work_type_id} -> {name}")
            else:
                row.name = name
                print(f"  sync  {work_type_id} -> {name}")

        db.commit()
        print(f"\nDone. {created} work type(s) created.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
