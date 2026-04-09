"""Seed demo users into the database.

Run once after alembic upgrade:
    python -m scripts.seed_users

Users created:
    +7 (900) 000-00-00 / demo  → Начальник ПТО (admin)
    +7 (900) 000-00-01 / demo  → Алексей (contractor)
    +7 (900) 000-00-02 / demo  → Никита  (contractor)
"""
from __future__ import annotations

import sys
import uuid

# Ensure project root is on path when running as script
sys.path.insert(0, ".")

from app.application.auth.security import hash_password
from app.infrastructure.database import SessionLocal
from app.infrastructure.users.models import UserModel

DEMO_USERS = [
    {"phone": "+7 (900) 000-00-00", "name": "Начальник ПТО", "password": "demo", "role": "admin"},
    {"phone": "+7 (900) 000-00-01", "name": "Алексей", "password": "demo", "role": "contractor"},
    {"phone": "+7 (900) 000-00-02", "name": "Никита",  "password": "demo", "role": "contractor"},
]


def seed() -> None:
    db = SessionLocal()
    try:
        created = 0
        for u in DEMO_USERS:
            exists = db.query(UserModel).filter(UserModel.phone == u["phone"]).first()
            if exists:
                print(f"  skip  {u['phone']} — already exists")
                continue
            row = UserModel(
                id=str(uuid.uuid4()),
                name=u["name"],
                phone=u["phone"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                is_active=True,
            )
            db.add(row)
            created += 1
            print(f"  added {u['phone']} ({u['name']})")
        db.commit()
        print(f"\nDone. {created} user(s) created.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
