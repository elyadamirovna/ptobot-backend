"""Domain entity for a user (contractor / manager)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class User:
    id: str
    name: str
    phone: str
    hashed_password: str
    role: str = "contractor"
    is_active: bool = True
