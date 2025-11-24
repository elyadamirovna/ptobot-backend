"""Pydantic models for work types."""

from __future__ import annotations

from pydantic import BaseModel


class WorkType(BaseModel):
    id: int
    name: str
