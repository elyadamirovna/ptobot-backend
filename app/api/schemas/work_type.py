"""Response schemas for work types."""
from __future__ import annotations

from pydantic import BaseModel

from app.domain.entities.work_type import WorkType
from dataclasses import asdict


class WorkTypeRead(BaseModel):
    id: str
    name: str

    @classmethod
    def from_entity(cls, work_type: WorkType) -> "WorkTypeRead":
        return cls(**asdict(work_type))
