"""Root response schema."""
from __future__ import annotations

from pydantic import BaseModel


class RootInfo(BaseModel):
    status: str
    message: str
    docs_url: str
    work_types_url: str
    reports_url: str
