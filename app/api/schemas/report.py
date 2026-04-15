"""Request and response schemas for reports."""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import List

from fastapi import Form
from pydantic import BaseModel, Field, constr, model_validator

from app.domain.entities.report import Report
from dataclasses import asdict


class ReportWorkItemPayload(BaseModel):
    work_type_id: constr(min_length=1, max_length=64) = Field(..., description="Type of work performed")
    description: constr(max_length=2000) = Field("", description="Work item description")
    people: constr(max_length=256) = Field("", description="People involved")
    volume: constr(max_length=256) = Field("", description="Work volume")
    machines: constr(max_length=256) = Field("", description="Machines used")
    sort_order: int = Field(default=0, ge=0)


class ReportCreate(BaseModel):
    site_id: constr(min_length=1, max_length=64) = Field(..., description="Identifier of the construction site")
    work_type_id: str = Field("", description="Primary type of work performed")
    report_date: date = Field(..., description="Date when work was performed")
    description: constr(max_length=2000) = Field("", description="Free-form description")
    people: constr(max_length=256) = Field("", description="People involved")
    volume: constr(max_length=256) = Field("", description="Work volume")
    machines: constr(max_length=256) = Field("", description="Machines used")
    work_items: List[ReportWorkItemPayload] = Field(default_factory=list, description="Structured work items")

    @model_validator(mode="after")
    def ensure_primary_work_type(self) -> "ReportCreate":
        if not self.work_type_id and self.work_items:
            self.work_type_id = self.work_items[0].work_type_id
        if not self.work_type_id:
            raise ValueError("work_type_id or work_items is required")
        return self

    @classmethod
    def as_form(
        cls,
        site_id: str = Form(...),
        work_type_id: str = Form(""),
        report_date: date = Form(...),
        description: str = Form(""),
        people: str = Form(""),
        volume: str = Form(""),
        machines: str = Form(""),
        payload: str | None = Form(default=None),
    ) -> "ReportCreate":
        if payload:
            return cls.model_validate(json.loads(payload))
        return cls(
            site_id=site_id,
            work_type_id=work_type_id,
            report_date=report_date,
            description=description,
            people=people,
            volume=volume,
            machines=machines,
        )


class ReportRead(BaseModel):
    id: str
    user_id: str
    site_id: str
    work_type_id: str
    report_date: date
    description: str
    people: str
    volume: str
    machines: str
    created_at: datetime
    photo_urls: List[str]
    work_items: List[ReportWorkItemPayload] = Field(default_factory=list)

    @classmethod
    def from_entity(cls, report: Report) -> "ReportRead":
        return cls(**asdict(report))


class ReportUpdate(BaseModel):
    work_type_id: str = Field("", description="Primary type of work performed")
    report_date: date = Field(..., description="Date when work was performed")
    description: constr(max_length=2000) = Field("", description="Free-form description")
    people: constr(max_length=256) = Field("", description="People involved")
    volume: constr(max_length=256) = Field("", description="Work volume")
    machines: constr(max_length=256) = Field("", description="Machines used")
    keep_photo_urls: List[str] = Field(default_factory=list)
    work_items: List[ReportWorkItemPayload] = Field(default_factory=list)

    @model_validator(mode="after")
    def ensure_primary_work_type(self) -> "ReportUpdate":
        if not self.work_type_id and self.work_items:
            self.work_type_id = self.work_items[0].work_type_id
        if not self.work_type_id:
            raise ValueError("work_type_id or work_items is required")
        return self
