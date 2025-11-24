"""Pydantic schemas used across the application."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class WorkTypeOut(BaseModel):
    id: int
    name: str


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


class RootInfo(BaseModel):
    """Ответ на запрос корневого URL для быстрой диагностики."""

    status: str
    message: str
    docs_url: str
    work_types_url: str
    reports_url: str
