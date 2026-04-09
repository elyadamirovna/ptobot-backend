"""Routes for reports creation and listing."""
from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.api.deps import ReportCreateForm, get_report_service, get_site_service
from app.api.schemas import ReportRead
from app.api.security import get_current_user
from app.application import ReportCreateCommand, ReportService, SiteService
from app.domain.entities import User

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead)
async def create_report(
    payload: ReportCreateForm,
    current_user: Annotated[User, Depends(get_current_user)],
    site_service: Annotated[SiteService, Depends(get_site_service)],
    photos: List[UploadFile] = File(..., description="List of photo files", min_items=1),
    report_service: ReportService = Depends(get_report_service),
) -> ReportRead:
    if current_user.role != "contractor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Отправка отчётов доступна только подрядчикам",
        )

    site_service.get_site_for_user(site_id=payload.site_id, user=current_user)

    command = ReportCreateCommand(user_id=current_user.id, **payload.model_dump())
    report = await report_service.create_report(command, photos)
    return ReportRead.from_entity(report)


@router.get("", response_model=List[ReportRead])
async def list_reports(
    site_id: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    work_type_id: Optional[str] = Query(default=None),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    report_service: ReportService = Depends(get_report_service),
) -> List[ReportRead]:
    if current_user.role != "admin":
        user_id = current_user.id
    reports = await report_service.list_reports(site_id=site_id, user_id=user_id, work_type_id=work_type_id)
    return [ReportRead.from_entity(report) for report in reports]
