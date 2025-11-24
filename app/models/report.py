"""Pydantic schemas for reports."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class ReportOut(BaseModel):
    id: int
    user_id: str
    work_type_id: str
    description: str
    people: str
    volume: str
    machines: str
    created_at: str
    photo_urls: List[str]
