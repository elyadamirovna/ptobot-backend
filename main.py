"""FastAPI backend for Ptobot."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import create_router
from app.bot.telegram import start_bot
from app.config import BOT_TASK_ATTR, MAX_REPORTS, YC_S3_BUCKET, create_s3_client
from app.repositories.report_repository import ReportRepository
from app.repositories.work_type_repository import WorkTypeRepository
from app.services.report_service import ReportService
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Ptobot backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    report_repo = ReportRepository(max_reports=MAX_REPORTS)
    storage_service = StorageService(client=create_s3_client(), bucket=YC_S3_BUCKET)
    report_service = ReportService(repository=report_repo, storage=storage_service)
    work_type_repo = WorkTypeRepository()

    router = create_router(report_service=report_service, work_type_repo=work_type_repo)
    app.include_router(router)

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

    return app


app = create_app()
