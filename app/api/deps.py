"""Dependency providers for FastAPI routes."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.repositories.report_repo import ReportRepository
from app.repositories.work_type_repo import WorkTypeRepository
from app.services.bot_service import BotService
from app.services.report_service import ReportService
from app.services.storage_service import StorageService


@lru_cache
def get_settings_dep() -> Settings:
    return get_settings()


@lru_cache
def get_work_type_repository() -> WorkTypeRepository:
    return WorkTypeRepository()


@lru_cache
def get_report_repository() -> ReportRepository:
    settings = get_settings_dep()
    return ReportRepository(limit=settings.reports_limit)


@lru_cache
def get_storage_service() -> StorageService:
    settings = get_settings_dep()
    return StorageService(settings)


def get_report_service() -> ReportService:
    return ReportService(get_report_repository(), get_storage_service())


def get_bot_service() -> BotService:
    return BotService(get_settings_dep())
