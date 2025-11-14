import os
import uuid
import datetime as dt
from typing import List, Optional

import aiofiles
from fastapi import FastAPI, UploadFile, File, Form, Query
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
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Размер блока для потоковой записи файлов (1 МБ)
UPLOAD_CHUNK_SIZE = 1024 * 1024

# Простое хранилище в памяти (пока без базы)
REPORTS: List[ReportOut] = []

# CORS, чтобы фронт и WebApp могли стучаться
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],          # при желании можно сузить до домена фронта
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Раздача файлов по /uploads/...
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ---------- Виды работ ----------

@app.get("/work_types", response_model=List[WorkTypeOut])
async def get_work_types():
  """
  Справочник видов работ.
  Пока захардкожен. Можно потом брать из БД.
  """
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
  user_id: str = Form(...),
  work_type_id: str = Form(...),
  description: str = Form(""),
  people: str = Form(""),
  volume: str = Form(""),
  machines: str = Form(""),
  photos: List[UploadFile] = File(...),  # несколько файлов
):
  """
  Создаёт отчёт и сохраняет все приложенные фото.
  Фронт должен слать поля FormData:
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
    # расширение файла
    ext = os.path.splitext(photo.filename or "")[1] or ".jpg"
    # уникальное имя
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # сохраняем файл порциями, чтобы не держать всё содержимое в памяти
    await _save_upload_file(photo, file_path)

    photo_urls.append(f"/uploads/{filename}")

  report_id = len(REPORTS) + 1
  created_at = dt.datetime.utcnow().isoformat()

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
  user_id: Optional[str] = Query(None),
  work_type_id: Optional[str] = Query(None),
):
  """
  Возвращает список отчётов из памяти.
  Пока фильтрация очень простая:
    - по user_id (если передан)
    - по work_type_id (если передан)
  """
  return [
    report
    for report in REPORTS
    if (user_id is None or report.user_id == user_id)
    and (work_type_id is None or report.work_type_id == work_type_id)
  ]


# ---------- Корень ----------

@app.get("/")
async def root():
  return {"status": "ok", "message": "Ptobot backend is running"}
