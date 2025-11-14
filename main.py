"""FastAPI backend for Ptobot."""

from __future__ import annotations

import datetime as dt
import os
import uuid
from collections import deque
from itertools import count
from pathlib import Path
from typing import Deque, List, Optional

from fastapi import File, Form, FastAPI, HTTPException, Query, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------- Модели ----------


class WorkTypeOut(BaseModel):
    id: int
    name: str


class ReportOut(BaseModel):
    id: int
    user_id: str
    work_type_id: str
    description: str
    people: str
    volume: str
    machines: str
    created_at: str
    photo_urls: List[str]


# ---------- Настройки ----------

app = FastAPI(title="Ptobot backend")

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

try:
    MAX_REPORTS = int(os.getenv("MAX_REPORTS", "500"))
except ValueError:
    MAX_REPORTS = 500

WORK_TYPES: List[WorkTypeOut] = [
    WorkTypeOut(id=1, name="Земляные работы"),
    WorkTypeOut(id=2, name="Бетонирование"),
    WorkTypeOut(id=3, name="Монтаж конструкций"),
]

REPORTS: Deque[ReportOut] = deque(maxlen=MAX_REPORTS)
REPORT_ID_COUNTER = count(1)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ---------- Виды работ ----------


@app.get("/work_types", response_model=List[WorkTypeOut])
async def get_work_types() -> List[WorkTypeOut]:
    """Возвращает справочник видов работ."""

    return WORK_TYPES


# ---------- Создание отчёта ----------


@app.post("/reports", response_model=ReportOut)
async def create_report(
    request: Request,
    user_id: str = Form(...),
    work_type_id: str = Form(...),
    description: str = Form(""),
    people: str = Form(""),
    volume: str = Form(""),
    machines: str = Form(""),
    photos: List[UploadFile] = File(...),
) -> ReportOut:
    """Создать отчёт и сохранить все приложенные фото."""

    if not photos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нужно приложить хотя бы одно фото",
        )

    photo_urls: List[str] = []

    for photo in photos:
        ext = Path(photo.filename or "").suffix or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / filename

        content = await photo.read()
        file_path.write_bytes(content)

        photo_url = request.url_for("uploads", path=filename)
        photo_urls.append(str(photo_url))

    report_id = next(REPORT_ID_COUNTER)
    created_at = dt.datetime.now(dt.timezone.utc).isoformat()

    report = ReportOut(
        id=report_id,
        user_id=user_id,
        work_type_id=str(work_type_id),
        description=description,
        people=people,
        volume=volume,
        machines=machines,
        created_at=created_at,
        photo_urls=photo_urls,
    )

    REPORTS.append(report)
    return report


# ---------- Получение списка отчётов ----------


@app.get("/reports", response_model=List[ReportOut])
async def list_reports(
    user_id: Optional[str] = Query(default=None),
    work_type_id: Optional[str] = Query(default=None),
) -> List[ReportOut]:
    """Вернуть список отчётов, отфильтрованных по user_id и work_type."""

    reports = list(REPORTS)
    if user_id is not None:
        reports = [r for r in reports if r.user_id == user_id]
    if work_type_id is not None:
        reports = [r for r in reports if r.work_type_id == work_type_id]
    return reports


# ---------- Корень ----------


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "message": "Ptobot backend is running"}
