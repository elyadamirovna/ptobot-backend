"""Read model for site report history."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List


@dataclass(slots=True)
class ReportHistoryItem:
    id: str
    site_id: str
    work_type_id: str
    work_type_name: str
    report_date: date
    created_at: datetime
    description: str
    people: str
    volume: str
    machines: str
    photo_urls: List[str] = field(default_factory=list)
    author_id: str = ""
    author_name: str = ""
