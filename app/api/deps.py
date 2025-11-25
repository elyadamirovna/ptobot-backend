"""Dependency providers for FastAPI routes."""
from __future__ import annotations

from functools import cached_property
from typing import Annotated

from fastapi import Depends, Request

from app.api.schemas import ReportCreate
from app.application import ReportService, WorkTypeService
from app.config import Settings
from app.domain.ports import UtcClock
from app.infrastructure import InMemoryReportRepository, InMemoryWorkTypeRepository, YandexStorage
from app.services.bot_service import BotService


class AppContainer:
    """Lightweight container to hold shared services for the app lifespan."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @cached_property
    def clock(self) -> UtcClock:
        return UtcClock()

    @cached_property
    def storage(self) -> YandexStorage:
        return YandexStorage(self.settings)

    @cached_property
    def report_repository(self) -> InMemoryReportRepository:
        return InMemoryReportRepository(limit=self.settings.reports_limit)

    @cached_property
    def work_type_repository(self) -> InMemoryWorkTypeRepository:
        return InMemoryWorkTypeRepository()

    @cached_property
    def report_service(self) -> ReportService:
        return ReportService(
            repository=self.report_repository,
            storage=self.storage,
            clock=self.clock,
        )

    @cached_property
    def work_type_service(self) -> WorkTypeService:
        return WorkTypeService(self.work_type_repository)

    @cached_property
    def bot_service(self) -> BotService:
        return BotService(self.settings)


async def get_container(request: Request) -> AppContainer:
    return request.app.state.container  # type: ignore[attr-defined]


def get_settings(container: Annotated[AppContainer, Depends(get_container)]) -> Settings:
    return container.settings


def get_report_service(container: Annotated[AppContainer, Depends(get_container)]) -> ReportService:
    return container.report_service


def get_work_type_service(container: Annotated[AppContainer, Depends(get_container)]) -> WorkTypeService:
    return container.work_type_service


def get_bot_service(container: Annotated[AppContainer, Depends(get_container)]) -> BotService:
    return container.bot_service


ReportCreateForm = Annotated[ReportCreate, Depends(ReportCreate.as_form)]
