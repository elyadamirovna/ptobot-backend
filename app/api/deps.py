"""Dependency providers for FastAPI."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, settings
from app.infrastructure.yandex_s3 import create_s3_client
from app.repositories.report_repo import ReportRepository
from app.repositories.work_type_repo import WorkTypeRepository
from app.services.bot_service import BotService
from app.services.report_service import ReportService
from app.services.storage_service import StorageService


@lru_cache()
def get_settings() -> Settings:
    return settings


@lru_cache()
def get_work_type_repo() -> WorkTypeRepository:
    return WorkTypeRepository()


@lru_cache()
def get_report_repo(settings: Settings | None = None) -> ReportRepository:
    cfg = settings or get_settings()
    return ReportRepository(max_reports=cfg.max_reports)


@lru_cache()
def get_s3_client():
    return create_s3_client(get_settings())


@lru_cache()
def get_storage_service(settings: Settings | None = None) -> StorageService:
    cfg = settings or get_settings()
    return StorageService(get_s3_client(), cfg)


@lru_cache()
def get_report_service() -> ReportService:
    return ReportService(get_report_repo(), get_storage_service())


@lru_cache()
def get_bot_service() -> BotService:
    cfg = get_settings()
    return BotService(bot_token=cfg.bot_token)
