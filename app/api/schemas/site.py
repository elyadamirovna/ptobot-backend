"""Response schemas for sites."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.domain.entities.site import Site


class SiteWrite(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=255)
    contractor_id: str | None = Field(default=None, max_length=64)
    pto_engineer_id: str | None = Field(default=None, max_length=64)


class SiteRead(BaseModel):
    id: str
    name: str
    address: str
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
            contractor_id=site.contractor_id,
            contractor_name=site.contractor_name,
            pto_engineer_id=site.pto_engineer_id,
            pto_engineer_name=site.pto_engineer_name,
            last_report_date=site.last_report_date,
            has_today_report=site.has_today_report,
            status=site.status,
        )
