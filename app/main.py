"""FastAPI application entry point."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import reports, root, work_types
from app.config import get_settings
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging()
    app = FastAPI(title=settings.app_title)
    print("DEBUG DATABASE_URL =", settings.database_url, flush=True)
    logging.getLogger(__name__).info("CORS allow_origins: %s", settings.cors_allow_origins)
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
