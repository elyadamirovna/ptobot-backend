"""Port definition for user persistence."""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from app.domain.entities.user import User


@runtime_checkable
class UserRepository(Protocol):
    def get_by_id(self, user_id: str) -> Optional[User]:
        ...

    def get_by_phone(self, phone: str) -> Optional[User]:
        ...

    def add(self, user: User) -> User:
        ...

    def update(self, user: User) -> User | None:
        ...

    def list_all_by_role(self, role: str) -> list[User]:
        ...

    def list_contractors(self) -> list[User]:
        ...

    def list_by_role(self, role: str) -> list[User]:
        ...
