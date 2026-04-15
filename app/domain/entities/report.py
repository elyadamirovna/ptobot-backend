"""Domain entity for a report."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List

from .report_work_item import ReportWorkItem


@dataclass(slots=True)
class Report:
    id: str
    user_id: str
    site_id: str
    work_type_id: str
    report_date: date
    description: str
    people: str
    volume: str
    machines: str
    created_at: datetime
    photo_urls: List[str] = field(default_factory=list)
    work_items: List[ReportWorkItem] = field(default_factory=list)
