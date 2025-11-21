"""FastAPI backend for Ptobot with Yandex Object Storage uploads."""

from __future__ import annotations

import asyncio
import contextlib
import datetime as dt
import logging
import os
from collections import deque
from itertools import count
from typing import Deque, List, Optional

from fastapi import File, Form, FastAPI, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import boto3
from botocore.config import Config

from bot import start_bot

# ---------- Логгер ----------

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------- Модели ответа ----------


class WorkTypeOut(BaseModel):
  id: int
  name: str


class ReportOut(BaseModel):
  id: int
  user_id: str
  project_id: str
  work_type_id: str
  description: str
  people: str
  volume: str
  machines: str
  date: str
  created_at: str
  photo_urls: List[str]


class RootInfo(BaseModel):
  status: str
  message: str
  docs_url: str
  work_types_url: str
  reports_url: str


# ---------- Настройки приложения ----------

app = FastAPI(title="Ptobot backend")

# CORS (фронт у тебя на другом домене)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Память для временного хранения отчётов (потом вынесем в PostgreSQL)
MAX_REPORTS = 500
REPORTS: Deque[ReportOut] = deque(maxlen=MAX_REPORTS)
REPORT_ID_COUNTER = count(1)
BOT_TASK_ATTR = "bot_task"


# ---------- Настройки Yandex Object Storage ----------

YC_S3_ENDPOINT = os.getenv("YC_S3_ENDPOINT", "https://storage.yandexcloud.net")
YC_S3_BUCKET = os.getenv("YC_S3_BUCKET", "ptobot-photos")  # имя твоего бакета
YC_S3_ACCESS_KEY = os.getenv("YC_S3_ACCESS_KEY")
YC_S3_SECRET_KEY = os.getenv("YC_S3_SECRET_KEY")

if not (YC_S3_ACCESS_KEY and YC_S3_SECRET_KEY and YC_S3_BUCKET):
  logger.warning(
    "Yandex Object Storage credentials are not fully set. "
    "Photo upload will NOT work until YC_S3_ACCESS_KEY, YC_S3_SECRET_KEY, "
    "YC_S3_BUCKET are provided."
  )

s3_config = Config(
  signature_version="s3v4",
  retries={
    "max_attempts": 3,
    "mode": "standard",
  },
)

s3_client = boto3.client(
  "s3",
  endpoint_url=YC_S3_ENDPOINT,
  aws_access_key_id=YC_S3_ACCESS_KEY,
  aws_secret_access_key=YC_S3_SECRET_KEY,
  config=s3_config,
)


async def upload_photo_to_s3(photo: UploadFile, key: str) -> str:
  """
  Загружает файл в Yandex Object Storage и возвращает публичный URL.
  Выполняется в отдельном потоке, чтобы не блокировать event loop.
  """

  def _sync_upload() -> None:
    photo.file.seek(0)
    extra_args = {
      "ACL": "public-read",  # так объект будет доступен по прямой ссылке
      "ContentType": photo.content_type or "application/octet-stream",
    }
    s3_client.upload_fileobj(photo.file, YC_S3_BUCKET, key, ExtraArgs=extra_args)

  await asyncio.to_thread(_sync_upload)

  # стандартный публичный URL в YOS:
  return f"https://{YC_S3_BUCKET}.storage.yandexcloud.net/{key}"


# ---------- Telegram bot запуск / остановка ----------


@app.on_event("startup")
async def start_bot_task() -> None:
  """Запускаем Telegram-бота вместе с FastAPI."""

  bot_token = os.getenv("BOT_TOKEN")
  if not bot_token:
    logger.warning("BOT_TOKEN is not set, Telegram bot will not be started")
    setattr(app.state, BOT_TASK_ATTR, None)
    return

  task = asyncio.create_task(start_bot(bot_token))
  setattr(app.state, BOT_TASK_ATTR, task)


@app.on_event("shutdown")
async def stop_bot_task() -> None:
  """Останавливаем Telegram-бота при выключении приложения."""

  bot_task = getattr(app.state, BOT_TASK_ATTR, None)
  if not bot_task:
    return

  bot_task.cancel()
  with contextlib.suppress(asyncio.CancelledError):
    await bot_task


# ---------- Справочник видов работ ----------


@app.get("/work_types", response_model=List[WorkTypeOut])
async def get_work_types() -> List[WorkTypeOut]:
  """Возвращает справочник видов работ."""

  return [
    WorkTypeOut(id=1, name="Земляные работы"),
    WorkTypeOut(id=2, name="Бетонирование"),
    WorkTypeOut(id=3, name="Монтаж конструкций"),
  ]


# ---------- Создание отчёта ----------


@app.post("/reports", response_model=ReportOut)
async def create_report(
  request: Request,
  user_id: str = Form(...),
  project_id: str = Form(...),
  work_type_id: str = Form(...),
  date: str = Form(...),  # yyyy-mm-dd
  description: str = Form(""),
  people: str = Form(""),
  volume: str = Form(""),
  machines: str = Form(""),
  photos: List[UploadFile] = File(...),
) -> ReportOut:
  """
  Создать отчёт и выгрузить все фото в Yandex Object Storage.

  FormData от фронта:
    - user_id
    - project_id
    - work_type_id
    - date (строка YYYY-MM-DD)
    - description
    - people
    - volume
    - machines
    - photos[] (несколько файлов)
  """

  if not (YC_S3_ACCESS_KEY and YC_S3_SECRET_KEY and YC_S3_BUCKET):
    raise RuntimeError(
      "Yandex Object Storage is not configured. "
      "Set YC_S3_ACCESS_KEY, YC_S3_SECRET_KEY, YC_S3_BUCKET env vars."
    )

  photo_urls: List[str] = []

  for idx, photo in enumerate(photos):
    # ключ в бакете: reports/{yyyy}/{mm}/{dd}/{uuid}-{idx}.ext
    ext = (os.path.splitext(photo.filename or "")[1] or ".jpg").lower()
    today = dt.date.fromisoformat(date)
    key = (
      f"reports/{today.year}/{today.month:02d}/{today.day:02d}/"
      f"{user_id}-{next(REPORT_ID_COUNTER)}-{idx}{ext}"
    )

    url = await upload_photo_to_s3(photo, key)
    photo_urls.append(url)

  # Поскольку я использовал REPORT_ID_COUNTER при ключах, для отчёта нужен отдельный id
  report_id = next(REPORT_ID_COUNTER)
  created_at = dt.datetime.now(dt.timezone.utc).isoformat()

  report = ReportOut(
    id=report_id,
    user_id=user_id,
    project_id=project_id,
    work_type_id=str(work_type_id),
    description=description,
    people=people,
    volume=volume,
    machines=machines,
    date=date,
    created_at=created_at,
    photo_urls=photo_urls,
  )

  REPORTS.append(report)
  return report


# ---------- История отчётов ----------


@app.get("/reports", response_model=List[ReportOut])
async def list_reports(
  user_id: Optional[str] = Query(default=None),
  project_id: Optional[str] = Query(default=None),
  work_type_id: Optional[str] = Query(default=None),
) -> List[ReportOut]:
  """
  Список отчётов, с фильтрами по user_id / project_id / work_type_id.
  Пока данные лежат в памяти (deque), позже всё перенесём в PostgreSQL.
  """

  result: List[ReportOut] = list(REPORTS)

  if user_id is not None:
    result = [r for r in result if r.user_id == user_id]
  if project_id is not None:
    result = [r for r in result if r.project_id == project_id]
  if work_type_id is not None:
    result = [r for r in result if r.work_type_id == work_type_id]

  # можно добавить сортировку по дате создания (самые новые сверху)
  result.sort(key=lambda r: r.created_at, reverse=True)
  return result


# ---------- Корень ----------


@app.get("/", response_model=RootInfo)
async def root() -> RootInfo:
  base = "/"
  return RootInfo(
    status="ok",
    message="Ptobot backend is running",
    docs_url=f"{base}docs",
    work_types_url=f"{base}work_types",
    reports_url=f"{base}reports",
  )
