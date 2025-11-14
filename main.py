"""FastAPI backend for Ptobot."""

from __future__ import annotations

import datetime as dt
import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import File, Form, FastAPI, Query, Request, UploadFile
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


# ---------- Инициализация приложения ----------

app = FastAPI(title="Ptobot backend")

# Папка для сохранения фото
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Размер блока для потоковой записи файлов (1 МБ)
UPLOAD_CHUNK_SIZE = 1024 * 1024

# Простое хранилище в памяти (пока без базы)
REPORTS: List[ReportOut] = []

# CORS, чтобы фронт и WebApp могли стучаться
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # при желании можно сузить до домена фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздача файлов по /uploads/...
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ---------- Виды работ ----------

@app.get("/work_types", response_model=List[WorkTypeOut])
async def get_work_types() -> List[WorkTypeOut]:
    """Возвращает справочник видов работ."""

    return [
        WorkTypeOut(id=1, name="Земляные работы"),
        WorkTypeOut(id=2, name="Бетонирование"),
        WorkTypeOut(id=3, name="Монтаж конструкций"),
    ]


# ---------- Создание отчёта ----------

async def _save_upload_file(upload_file: UploadFile, destination_path: str) -> None:
  """Сохраняет загруженный файл на диск, записывая его порциями."""

  async with aiofiles.open(destination_path, "wb") as destination:
    while True:
      chunk = await upload_file.read(UPLOAD_CHUNK_SIZE)
      if not chunk:
        break
      await destination.write(chunk)

  await upload_file.close()


@app.post("/reports", response_model=ReportOut)
async def create_report(
    request: Request,
    user_id: str = Form(...),
    work_type_id: str = Form(...),
    description: str = Form(""),
    people: str = Form(""),
    volume: str = Form(""),
    machines: str = Form(""),
    photos: List[UploadFile] = File(...),  # несколько файлов
) -> ReportOut:
    """
    Создать отчёт и сохранить все приложенные фото.

    Фронт должен отправить поля FormData:
      - user_id
      - work_type_id
      - description
      - people
      - volume
      - machines
      - photos (несколько файлов)
    """

    photo_urls: List[str] = []

    for photo in photos:
        ext = Path(photo.filename or "").suffix or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / filename

        content = await photo.read()
        file_path.write_bytes(content)

        photo_url = request.url_for("uploads", path=filename)
        photo_urls.append(str(photo_url))

    report_id = len(REPORTS) + 1
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


# ---------- Получение списка отчётов (для истории/сводки) ----------

@app.get("/reports", response_model=List[ReportOut])
async def list_reports(
    user_id: Optional[str] = Query(default=None),
    work_type_id: Optional[str] = Query(default=None),
) -> List[ReportOut]:
    """Вернуть список отчётов, отфильтрованных по user_id и work_type."""

    result = REPORTS
    if user_id is not None:
        result = [r for r in result if r.user_id == user_id]
    if work_type_id is not None:
        result = [r for r in result if r.work_type_id == work_type_id]
    return result


# ---------- Корень ----------

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "message": "Ptobot backend is running"}
