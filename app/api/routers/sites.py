"""Routes for construction sites."""
from __future__ import annotations

from datetime import date
from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_report_history_service, get_site_service
from app.api.schemas import SiteRead, SiteReportHistoryItemRead, SiteWrite
from app.api.security import get_current_user
from app.application import ReportHistoryService, SiteService
from app.domain.entities import User

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=List[SiteRead])
def list_sites(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SiteService, Depends(get_site_service)],
) -> List[SiteRead]:
    sites = service.list_sites_for_user(current_user)
    return [SiteRead.from_entity(site) for site in sites]


@router.post("", response_model=SiteRead, status_code=status.HTTP_201_CREATED)
def create_site(
    body: SiteWrite,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SiteService, Depends(get_site_service)],
) -> SiteRead:
    site = service.create_site(
        user=current_user,
        name=body.name,
        address=body.address,
        contractor_id=body.contractor_id,
    )
    return SiteRead.from_entity(site)


@router.patch("/{site_id}", response_model=SiteRead)
def update_site(
    site_id: str,
    body: SiteWrite,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SiteService, Depends(get_site_service)],
) -> SiteRead:
    site = service.update_site(
        user=current_user,
        site_id=site_id,
        name=body.name,
        address=body.address,
        contractor_id=body.contractor_id,
    )
    return SiteRead.from_entity(site)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(
    site_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SiteService, Depends(get_site_service)],
) -> Response:
    service.delete_site(user=current_user, site_id=site_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{site_id}/reports", response_model=List[SiteReportHistoryItemRead])
async def list_site_reports(
    site_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    history_service: Annotated[ReportHistoryService, Depends(get_report_history_service)],
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    work_type_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> List[SiteReportHistoryItemRead]:
    items = await history_service.get_site_report_history(
        user=current_user,
        site_id=site_id,
        date_from=date_from,
        date_to=date_to,
        work_type_id=work_type_id,
        limit=limit,
    )
    return [SiteReportHistoryItemRead.from_entity(item) for item in items]
