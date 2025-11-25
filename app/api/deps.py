"""Dependency providers for FastAPI routes."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.schemas import ReportCreate
from app.application import ReportService, WorkTypeService
from app.config import Settings, get_settings
from app.domain.ports import Clock, ReportRepository, StoragePort, UtcClock, WorkTypeRepository
from app.infrastructure import SqlAlchemyReportRepository, SqlAlchemyWorkTypeRepository, YandexStorage
from app.infrastructure.database import get_db

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_db)]


def get_clock() -> Clock:
    return UtcClock()


def get_storage(settings: SettingsDep) -> StoragePort:
    return YandexStorage(settings)


def get_report_repository(db: SessionDep) -> ReportRepository:
    return SqlAlchemyReportRepository(db)


def get_work_type_repository(db: SessionDep) -> WorkTypeRepository:
    return SqlAlchemyWorkTypeRepository(db)


def get_report_service(
    repository: Annotated[ReportRepository, Depends(get_report_repository)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    clock: Annotated[Clock, Depends(get_clock)],
) -> ReportService:
    return ReportService(repository=repository, storage=storage, clock=clock)


def get_work_type_service(
    repository: Annotated[WorkTypeRepository, Depends(get_work_type_repository)],
) -> WorkTypeService:
    return WorkTypeService(repository)


ReportCreateForm = Annotated[ReportCreate, Depends(ReportCreate.as_form)]
