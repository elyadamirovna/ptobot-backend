"""Pydantic schemas for work types."""

from __future__ import annotations

from pydantic import BaseModel


class WorkTypeOut(BaseModel):
    id: int
    name: str
