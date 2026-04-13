"""Dependency providers for FastAPI routes."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.schemas import ReportCreate
from app.application import ReportHistoryService, ReportService, SiteService, WorkTypeService
from app.config import Settings, get_settings
from app.domain.ports import Clock, ReportRepository, SiteRepository, StoragePort, UtcClock, UserRepository, WorkTypeRepository
from app.infrastructure import (
    SqlAlchemyReportRepository,
    SqlAlchemySiteRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyWorkTypeRepository,
    YandexStorage,
)
from app.infrastructure.database import get_db

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_db)]


def get_clock() -> Clock:
    return UtcClock()


def get_storage(settings: SettingsDep) -> StoragePort:
    return YandexStorage(settings)


def get_report_repository(db: SessionDep) -> ReportRepository:
    return SqlAlchemyReportRepository(db)


def get_site_repository(db: SessionDep) -> SiteRepository:
    return SqlAlchemySiteRepository(db)


def get_user_repository(db: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(db)


def get_work_type_repository(db: SessionDep) -> WorkTypeRepository:
    return SqlAlchemyWorkTypeRepository(db)


def get_report_service(
    repository: Annotated[ReportRepository, Depends(get_report_repository)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    clock: Annotated[Clock, Depends(get_clock)],
    site_service: Annotated[SiteService, Depends(get_site_service)],
) -> ReportService:
    return ReportService(repository=repository, storage=storage, clock=clock, site_service=site_service)


def get_report_history_service(
    repository: Annotated[ReportRepository, Depends(get_report_repository)],
    site_service: Annotated[SiteService, Depends(get_site_service)],
) -> ReportHistoryService:
    return ReportHistoryService(repository=repository, site_service=site_service)


def get_work_type_service(
    repository: Annotated[WorkTypeRepository, Depends(get_work_type_repository)],
) -> WorkTypeService:
    return WorkTypeService(repository)


def get_site_service(
    repository: Annotated[SiteRepository, Depends(get_site_repository)],
) -> SiteService:
    return SiteService(repository)


def get_user_service_repository(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserRepository:
    return repository


ReportCreateForm = Annotated[ReportCreate, Depends(ReportCreate.as_form)]
