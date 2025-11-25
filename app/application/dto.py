"""Application-layer DTOs for commands and queries."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReportCreateCommand:
    user_id: str
    work_type_id: str
    description: str
    people: str
    volume: str
    machines: str
