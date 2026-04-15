"""Domain entity for a single work item inside a report."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReportWorkItem:
    id: str = ""
    work_type_id: str = ""
    work_type_name: str = ""
    description: str = ""
    people: str = ""
    volume: str = ""
    machines: str = ""
    sort_order: int = 0
