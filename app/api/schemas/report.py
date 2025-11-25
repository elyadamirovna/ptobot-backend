"""Request and response schemas for reports."""
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import Form
from pydantic import BaseModel, Field, constr

from app.domain.entities.report import Report
from dataclasses import asdict


class ReportCreate(BaseModel):
    user_id: constr(min_length=1, max_length=128) = Field(..., description="Identifier of the reporter")
    work_type_id: constr(min_length=1, max_length=64) = Field(..., description="Type of work performed")
    description: constr(max_length=2000) = Field("", description="Free-form description")
    people: constr(max_length=256) = Field("", description="People involved")
    volume: constr(max_length=256) = Field("", description="Work volume")
    machines: constr(max_length=256) = Field("", description="Machines used")

    @classmethod
    def as_form(
        cls,
        user_id: str = Form(...),
        work_type_id: str = Form(...),
        description: str = Form(""),
        people: str = Form(""),
        volume: str = Form(""),
        machines: str = Form(""),
    ) -> "ReportCreate":
        return cls(
            user_id=user_id,
            work_type_id=work_type_id,
            description=description,
            people=people,
            volume=volume,
            machines=machines,
        )


class ReportRead(BaseModel):
    id: str
    user_id: str
    work_type_id: str
    description: str
    people: str
    volume: str
    machines: str
    created_at: datetime
    photo_urls: List[str]

    @classmethod
    def from_entity(cls, report: Report) -> "ReportRead":
        return cls(**asdict(report))
