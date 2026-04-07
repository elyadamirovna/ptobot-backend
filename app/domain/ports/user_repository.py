"""Port definition for user persistence."""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from app.domain.entities.user import User


@runtime_checkable
class UserRepository(Protocol):
    def get_by_phone(self, phone: str) -> Optional[User]:
        ...

    def add(self, user: User) -> User:
        ...
