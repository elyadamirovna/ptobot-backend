"""Routes for reports creation and listing."""
from __future__ import annotations

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.api.deps import ReportCreateForm, get_report_service
from app.api.schemas import ReportRead
from app.api.security import get_current_user
from app.application import ReportCreateCommand, ReportService
from app.domain.entities import User
from app.infrastructure.database import get_db
from app.infrastructure.sites import SqlAlchemySiteRepository
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead)
async def create_report(
    payload: ReportCreateForm,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    photos: List[UploadFile] = File(..., description="List of photo files", min_items=1),
    report_service: ReportService = Depends(get_report_service),
) -> ReportRead:
    if current_user.role != "contractor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Отправка отчётов доступна только подрядчикам",
        )

    site = SqlAlchemySiteRepository(db).get_by_id(payload.site_id)
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Объект не найден",
        )
    if site.contractor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к выбранному объекту",
        )

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
