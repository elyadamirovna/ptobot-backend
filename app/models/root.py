"""Root endpoint schema."""

from __future__ import annotations

from pydantic import BaseModel


class RootInfo(BaseModel):
    """Ответ на запрос корневого URL для быстрой диагностики."""

    status: str
    message: str
    docs_url: str
    work_types_url: str
    reports_url: str
