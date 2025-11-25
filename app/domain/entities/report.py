"""Domain entity for a report."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(slots=True)
class Report:
    id: str
    user_id: str
    work_type_id: str
    description: str
    people: str
    volume: str
    machines: str
    created_at: datetime
    photo_urls: List[str] = field(default_factory=list)
