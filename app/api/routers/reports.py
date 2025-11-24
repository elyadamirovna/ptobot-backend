"""Routes for reports creation and listing."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.api.deps import get_report_service
from app.models.report import ReportOut
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportOut)
async def create_report(
    user_id: str = Form(...),
    work_type_id: str = Form(...),
    description: str = Form(""),
    people: str = Form(""),
    volume: str = Form(""),
    machines: str = Form(""),
    photos: List[UploadFile] = File(...),
    report_service: ReportService = Depends(get_report_service),
) -> ReportOut:
    return await report_service.create_report(
        user_id=user_id,
        work_type_id=work_type_id,
        description=description,
        people=people,
        volume=volume,
        machines=machines,
        photos=photos,
    )


@router.get("", response_model=List[ReportOut])
async def list_reports(
    user_id: Optional[str] = Query(default=None),
    work_type_id: Optional[str] = Query(default=None),
    report_service: ReportService = Depends(get_report_service),
) -> List[ReportOut]:
    return report_service.list_reports(user_id=user_id, work_type_id=work_type_id)
