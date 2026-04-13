"""Domain entity for a construction site."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class Site:
    id: str
    name: str
    address: str
    contractor_id: str | None = None
    contractor_name: str | None = None
    pto_engineer_id: str | None = None
    pto_engineer_name: str | None = None
    last_report_date: date | None = None
    has_today_report: bool = False
    status: str = "missing"
