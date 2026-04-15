"""Domain entity for work types."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkType:
    id: str
    name: str
    parent_id: str | None = None
    sort_order: int = 0
    unit: str | None = None
    is_active: bool = True
    requires_volume: bool = False
    requires_people: bool = False
    requires_machines: bool = False
