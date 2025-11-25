"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import AppContainer
from app.api.routers import reports, root, work_types
from app.config import Settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.container = AppContainer(settings)

    bot_service = app.state.container.bot_service
    setup_logging()

    await bot_service.start(app)
    try:
        yield
    finally:
        await bot_service.stop(app)


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title=settings.app_title, lifespan=lifespan)

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

    return app


app = create_app()
