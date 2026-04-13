"""SQLAlchemy implementation of UserRepository."""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.infrastructure.users.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        row = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        if row is None:
            return None
        return self._to_entity(row)

    def get_by_phone(self, phone: str) -> Optional[User]:
        row = self._db.query(UserModel).filter(UserModel.phone == phone).first()
        if row is None:
            return None
        return self._to_entity(row)

    def add(self, user: User) -> User:
        row = UserModel(
            id=user.id,
            name=user.name,
            company_name=user.company_name,
            phone=user.phone,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    def update(self, user: User) -> User | None:
        row = self._db.query(UserModel).filter(UserModel.id == user.id).first()
        if row is None:
            return None

        row.name = user.name
        row.company_name = user.company_name
        row.phone = user.phone
        row.hashed_password = user.hashed_password
        row.role = user.role
        row.is_active = user.is_active
        self._db.commit()
        self._db.refresh(row)
        return self._to_entity(row)

    def list_contractors(self) -> list[User]:
        rows = self._db.execute(
            select(UserModel)
            .where(UserModel.role == "contractor", UserModel.is_active.is_(True))
            .order_by(UserModel.name.asc())
        ).scalars().all()
        return [self._to_entity(row) for row in rows]

    def list_all_by_role(self, role: str) -> list[User]:
        rows = self._db.execute(
            select(UserModel)
            .where(UserModel.role == role)
            .order_by(UserModel.name.asc())
        ).scalars().all()
        return [self._to_entity(row) for row in rows]

    def list_by_role(self, role: str) -> list[User]:
        rows = self._db.execute(
            select(UserModel)
            .where(UserModel.role == role, UserModel.is_active.is_(True))
            .order_by(UserModel.name.asc())
        ).scalars().all()
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(row: UserModel) -> User:
        return User(
            id=row.id,
            name=row.name,
            company_name=row.company_name,
            phone=row.phone,
            hashed_password=row.hashed_password,
            role=row.role,
            is_active=row.is_active,
        )
