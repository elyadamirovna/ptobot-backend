"""Routes for reports creation and listing."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.api.deps import ReportCreateForm, get_report_service
from app.api.schemas import ReportRead
from app.application import ReportCreateCommand, ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportRead)
async def create_report(
    payload: ReportCreateForm,
    photos: List[UploadFile] = File(..., description="List of photo files", min_items=1),
    report_service: ReportService = Depends(get_report_service),
) -> ReportRead:
    command = ReportCreateCommand(**payload.model_dump())
    report = await report_service.create_report(command, photos)
    return ReportRead.from_entity(report)


@router.get("", response_model=List[ReportRead])
async def list_reports(
    user_id: Optional[str] = Query(default=None),
    work_type_id: Optional[str] = Query(default=None),
    report_service: ReportService = Depends(get_report_service),
) -> List[ReportRead]:
    reports = await report_service.list_reports(user_id=user_id, work_type_id=work_type_id)
    return [ReportRead.from_entity(report) for report in reports]
