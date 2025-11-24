"""FastAPI backend for Ptobot."""

from __future__ import annotations

import asyncio
import contextlib
import datetime as dt
import uuid
import logging
import os
from collections import deque
from itertools import count
from pathlib import Path
from typing import Deque, List, Optional

import boto3
from fastapi import File, Form, FastAPI, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from bot import start_bot

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

class RootInfo(BaseModel):
    """Ответ на запрос корневого URL для быстрой диагностики."""
    status: str
    message: str
    docs_url: str
    work_types_url: str
    reports_url: str


# ---------- Настройки ----------

logger = logging.getLogger(__name__)
app = FastAPI(title="Ptobot backend")

MAX_REPORTS = 500
REPORTS: Deque[ReportOut] = deque(maxlen=MAX_REPORTS)
REPORT_ID_COUNTER = count(1)
BOT_TASK_ATTR = "bot_task"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Yandex Object Storage ----------

YC_S3_ENDPOINT = os.getenv("YC_S3_ENDPOINT", "https://storage.yandexcloud.net")
YC_S3_REGION = os.getenv("YC_S3_REGION", "ru-central1")
YC_S3_BUCKET = os.getenv("YC_S3_BUCKET", "ptobot-assets")

YC_S3_ACCESS_KEY_ID = os.getenv("YC_S3_ACCESS_KEY_ID")
YC_S3_SECRET_ACCESS_KEY = os.getenv("YC_S3_SECRET_ACCESS_KEY")

s3 = boto3.client(
    "s3",
    endpoint_url=YC_S3_ENDPOINT,
    region_name=YC_S3_REGION,
    aws_access_key_id=YC_S3_ACCESS_KEY_ID,
    aws_secret_access_key=YC_S3_SECRET_ACCESS_KEY,
)


async def upload_to_yandex(file: UploadFile) -> str:
    """Загружает файл в Yandex Object Storage и возвращает публичный URL."""

    ext = Path(file.filename or "").suffix or ".jpg"
    key = f"reports/{uuid.uuid4().hex}{ext}"

    content = await file.read()

    s3.put_object(
        Bucket=YC_S3_BUCKET,
        Key=key,
        Body=content,
        ContentType=file.content_type,
        ACL="public-read",
    )

    return f"https://{YC_S3_BUCKET}.storage.yandexcloud.net/{key}"


@app.on_event("startup")
async def start_bot_task() -> None:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.warning("BOT_TOKEN is not set, Telegram bot will not be started")
        setattr(app.state, BOT_TASK_ATTR, None)
        return

    task = asyncio.create_task(start_bot(bot_token))
    setattr(app.state, BOT_TASK_ATTR, task)

@app.on_event("shutdown")
async def stop_bot_task() -> None:
    bot_task: Optional[asyncio.Task] = getattr(app.state, BOT_TASK_ATTR, None)
    if not bot_task:
        return

    bot_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await bot_task

# ---------- Виды работ ----------

@app.get("/work_types", response_model=List[WorkTypeOut])
async def get_work_types() -> List[WorkTypeOut]:
    return [
        WorkTypeOut(id=1, name="Земляные работы"),
        WorkTypeOut(id=2, name="Бетонирование"),
        WorkTypeOut(id=3, name="Монтаж конструкций"),
    ]

# ---------- Создание отчёта ----------

@app.post("/reports", response_model=ReportOut)
async def create_report(
    user_id: str = Form(...),
    work_type_id: str = Form(...),
    description: str = Form(""),
    people: str = Form(""),
    volume: str = Form(""),
    machines: str = Form(""),
    photos: List[UploadFile] = File(...),
) -> ReportOut:

    photo_urls: List[str] = []

    # Загружаем в Yandex Cloud
    for photo in photos:
        url = await upload_to_yandex(photo)
        photo_urls.append(url)

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

# ---------- История отчётов ----------

@app.get("/reports", response_model=List[ReportOut])
async def list_reports(
    user_id: Optional[str] = Query(default=None),
    work_type_id: Optional[str] = Query(default=None),
) -> List[ReportOut]:

    result = REPORTS
    if user_id is not None:
        result = [r for r in result if r.user_id == user_id]
    if work_type_id is not None:
        result = [r for r in result if r.work_type_id == work_type_id]
    return result

# ---------- Корень ----------

@app.get("/", response_model=RootInfo)
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
