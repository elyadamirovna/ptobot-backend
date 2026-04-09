"""Response schemas for site report history."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from typing import List

from pydantic import BaseModel

from app.domain.entities import ReportHistoryItem


class SiteReportHistoryItemRead(BaseModel):
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
    photo_urls: List[str]
    author_id: str
    author_name: str

    @classmethod
    def from_entity(cls, item: ReportHistoryItem) -> "SiteReportHistoryItemRead":
        return cls(**asdict(item))
