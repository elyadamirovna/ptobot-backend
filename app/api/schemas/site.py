"""Response schemas for sites."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.domain.entities.site import Site


class SiteWrite(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=255)
    customer_name: str | None = Field(default=None, max_length=255)
    project_manager_name: str | None = Field(default=None, max_length=255)
    pto_responsible_name: str | None = Field(default=None, max_length=255)
    start_date: date | None = None
    planned_end_date: date | None = None
    budget_total: str | None = Field(default=None, max_length=255)
    budget_spent: str | None = Field(default=None, max_length=255)
    progress_percent: int | None = Field(default=None, ge=0, le=100)
    status_note: str | None = Field(default=None, max_length=2000)
    contractor_id: str | None = Field(default=None, max_length=64)
    pto_engineer_id: str | None = Field(default=None, max_length=64)


class SiteRead(BaseModel):
    id: str
    name: str
    address: str
    customer_name: str | None = None
    project_manager_name: str | None = None
    pto_responsible_name: str | None = None
    start_date: date | None = None
    planned_end_date: date | None = None
    budget_total: str | None = None
    budget_spent: str | None = None
    progress_percent: int | None = None
    status_note: str | None = None
    contractor_id: str | None = None
    contractor_name: str | None = None
    pto_engineer_id: str | None = None
    pto_engineer_name: str | None = None
    last_report_date: date | None = None
    has_today_report: bool = False
    status: str

    @classmethod
    def from_entity(cls, site: Site) -> "SiteRead":
        return cls(
            id=site.id,
            name=site.name,
            address=site.address,
            customer_name=site.customer_name,
            project_manager_name=site.project_manager_name,
            pto_responsible_name=site.pto_responsible_name,
            start_date=site.start_date,
            planned_end_date=site.planned_end_date,
            budget_total=site.budget_total,
            budget_spent=site.budget_spent,
            progress_percent=site.progress_percent,
            status_note=site.status_note,
            contractor_id=site.contractor_id,
            contractor_name=site.contractor_name,
            pto_engineer_id=site.pto_engineer_id,
            pto_engineer_name=site.pto_engineer_name,
            last_report_date=site.last_report_date,
            has_today_report=site.has_today_report,
            status=site.status,
        )
