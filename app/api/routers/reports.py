"""Routes for reports creation and listing."""
from __future__ import annotations

import json
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status

from app.api.deps import ReportCreateForm, get_report_service, get_site_service
from app.api.schemas import ReportRead, ReportUpdate
from app.api.security import get_current_user
from app.application import ReportCreateCommand, ReportService, ReportWorkItemCommand, SiteService
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

    command = ReportCreateCommand(
        user_id=current_user.id,
        site_id=payload.site_id,
        work_type_id=payload.work_type_id,
        report_date=payload.report_date,
        description=payload.description,
        people=payload.people,
        volume=payload.volume,
        machines=payload.machines,
        work_items=[
            ReportWorkItemCommand(
                work_type_id=item.work_type_id,
                description=item.description,
                people=item.people,
                volume=item.volume,
                machines=item.machines,
                sort_order=item.sort_order,
            )
            for item in payload.work_items
        ],
    )
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


@router.patch("/{report_id}", response_model=ReportRead)
async def update_report(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    report_service: ReportService = Depends(get_report_service),
    payload: str = File(..., description="JSON payload for report update"),
    photos: List[UploadFile] = File(default_factory=list),
) -> ReportRead:
    try:
        body = ReportUpdate.model_validate(json.loads(payload))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректные данные для обновления отчёта",
        ) from exc

    report = await report_service.update_report(
        report_id=report_id,
        user=current_user,
        work_type_id=body.work_type_id,
        report_date=body.report_date,
        description=body.description,
        people=body.people,
        volume=body.volume,
        machines=body.machines,
        keep_photo_urls=body.keep_photo_urls,
        new_photos=photos,
        work_items=body.work_items,
    )
    return ReportRead.from_entity(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    report_service: ReportService = Depends(get_report_service),
) -> Response:
    await report_service.delete_report(report_id=report_id, user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
