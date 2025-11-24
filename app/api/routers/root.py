"""Root endpoint router."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.models.root import RootInfo

router = APIRouter()


@router.get("/", response_model=RootInfo)
async def root(request: Request) -> RootInfo:
    """Ответ на корневой URL с ссылками на основные эндпоинты."""

    docs_url = str(request.url_for("swagger_ui_html"))
    work_types_url = str(request.url_for("list_work_types"))
    reports_url = str(request.url_for("list_reports"))

    return RootInfo(
        status="ok",
        message="Ptobot backend is running",
        docs_url=docs_url,
        work_types_url=work_types_url,
        reports_url=reports_url,
    )
