"""Application-layer DTOs for commands and queries."""
from __future__ import annotations

from datetime import date
from dataclasses import dataclass


@dataclass(slots=True)
class ReportCreateCommand:
    user_id: str
    site_id: str
    work_type_id: str
    report_date: date
    description: str
    people: str
    volume: str
    machines: str
