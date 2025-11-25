"""Domain entity for work types."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkType:
    id: str
    name: str
