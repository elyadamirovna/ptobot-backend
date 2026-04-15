"""Response schemas for work types."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.entities.work_type import WorkType
from dataclasses import asdict


class WorkTypeWrite(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: str | None = Field(default=None, max_length=64)
    sort_order: int = Field(default=0, ge=0)
    unit: str | None = Field(default=None, max_length=32)
    is_active: bool = True
    requires_volume: bool = False
    requires_people: bool = False
    requires_machines: bool = False


class WorkTypeRead(BaseModel):
    id: str
    name: str
    parent_id: str | None = None
    sort_order: int = 0
    unit: str | None = None
    is_active: bool = True
    requires_volume: bool = False
    requires_people: bool = False
    requires_machines: bool = False

    @classmethod
    def from_entity(cls, work_type: WorkType) -> "WorkTypeRead":
        return cls(**asdict(work_type))
