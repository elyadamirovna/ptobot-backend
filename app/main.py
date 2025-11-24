"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_bot_service, get_settings_dep
from app.api.routers import reports, root, work_types
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings_dep()

    app = FastAPI(title=settings.app_title)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(root.router)
    app.include_router(work_types.router)
    app.include_router(reports.router)

    bot_service = get_bot_service()

    @app.on_event("startup")
    async def start_bot_task() -> None:
        await bot_service.start(app)

    @app.on_event("shutdown")
    async def stop_bot_task() -> None:
        await bot_service.stop(app)

    return app


app = create_app()
