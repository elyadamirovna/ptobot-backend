"""API routes for the FastAPI application."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, File, Form, Query, Request, UploadFile

from app.models.schemas import ReportOut, RootInfo, WorkTypeOut
from app.repositories.work_type_repository import WorkTypeRepository
from app.services.report_service import ReportService


def create_router(
    report_service: ReportService, work_type_repo: WorkTypeRepository
) -> APIRouter:
    router = APIRouter()

    @router.get("/work_types", response_model=List[WorkTypeOut])
    async def get_work_types() -> List[WorkTypeOut]:
        return work_type_repo.get_all()

    @router.post("/reports", response_model=ReportOut)
    async def create_report(
        user_id: str = Form(...),
        work_type_id: str = Form(...),
        description: str = Form(""),
        people: str = Form(""),
        volume: str = Form(""),
        machines: str = Form(""),
        photos: List[UploadFile] = File(...),
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

    @router.get("/reports", response_model=List[ReportOut])
    async def list_reports(
        user_id: Optional[str] = Query(default=None),
        work_type_id: Optional[str] = Query(default=None),
    ) -> List[ReportOut]:
        return report_service.list_reports(user_id=user_id, work_type_id=work_type_id)

    @router.get("/", response_model=RootInfo)
    async def root(request: Request) -> RootInfo:
        """Ответ на корневой URL с ссылками на основные эндпоинты."""

        docs_url = str(request.url_for("swagger_ui_html"))
        work_types_url = str(request.url_for("get_work_types"))
        reports_url = str(request.url_for("list_reports"))

        return RootInfo(
            status="ok",
            message="Ptobot backend is running",
            docs_url=docs_url,
            work_types_url=work_types_url,
            reports_url=reports_url,
        )

    return router
