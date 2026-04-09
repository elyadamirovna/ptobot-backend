"""Seed construction sites into the database.

Run after alembic upgrade:
    python -m scripts.seed_sites
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from app.infrastructure.database import SessionLocal
from app.infrastructure.sites.models import SiteModel

SITE_NAMES = [
    "парковая 15-я ул.",
    "2-я Прядильная ул.",
    "Тюменская ул.",
    "Никитинская ул.",
    "Бойцовая ул.",
    "Измайловское шоссе (Измайлова)",
    "Уткина ул.",
    "Попов пр.",
    "Измайловское шоссе (район Соколиная Гора)",
    "Красковская улю",
    "8-го Марта ул.",
    "1-я Парковая ул.",
    "Подъездная дорога МСз",
    "Люксембург Розы ул.",
    "Аносова ул.",
    "Красковский туп.",
    "Парковка на пересечении Буракова и Ш. Энтузиастов",
    "2-й Кожуховский пер. (бывший 3-го Интернационала 2-й пер. )",
    "2-й Лихачевский переулок",
    "4-й Лихачевский переулок",
    "Белобородова Генерала вл. 38",
    "Веры Волошиной улица",
    "Летная ул.",
    'Машкинское шоссе ("Дорога в поселке "Юрма")',
    "Митинская улица (местный проезд)",
    "Михалковская улица",
    "Нарвская улица (Головинский район)",
    "улица Берзарина",
    "Улица Генерала Рычагова",
    "Сосновая улица",
]

DEMO_SITES = [
    {
        "id": f"site-{index}",
        "name": name,
        "address": name,
        "contractor_phone": None,
    }
    for index, name in enumerate(SITE_NAMES, start=1)
]


def seed() -> None:
    db = SessionLocal()
    try:
        created = 0
        updated = 0
        for site in DEMO_SITES:
            row = db.query(SiteModel).filter(SiteModel.id == site["id"]).first()
            if row is None:
                row = SiteModel(
                    id=site["id"],
                    name=site["name"],
                    address=site["address"],
                    contractor_id=None,
                )
                db.add(row)
                created += 1
                print(f"  added {site['name']}")
            else:
                row.name = site["name"]
                row.address = site["address"]
                row.contractor_id = None
                updated += 1
                print(f"  sync  {site['name']}")

        db.commit()
        print(f"\nDone. {created} site(s) created, {updated} updated.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
