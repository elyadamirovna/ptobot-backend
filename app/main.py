"""FastAPI application entrypoint."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_bot_service, get_settings
from app.api.routers import reports, root, work_types
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_title)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root.router)
app.include_router(work_types.router)
app.include_router(reports.router)


@app.on_event("startup")
async def start_bot_task() -> None:
    bot_service = get_bot_service()
    await bot_service.start()


@app.on_event("shutdown")
async def stop_bot_task() -> None:
    bot_service = get_bot_service()
    await bot_service.stop()
