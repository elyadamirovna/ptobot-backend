"""SQLAlchemy-based repository for reports."""
from __future__ import annotations

import uuid
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Report
from app.domain.ports import ReportRepository
from app.infrastructure.reports.models import ReportModel


class SqlAlchemyReportRepository(ReportRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    async def add(self, report: Report) -> Report:
        model = ReportModel(
            id=report.id,
            user_id=report.user_id,
            work_type_id=report.work_type_id,
            description=report.description,
            people=report.people,
            volume=report.volume,
            machines=report.machines,
            created_at=report.created_at,
            photo_urls=list(report.photo_urls),
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    async def list(self, *, user_id: str | None = None, work_type_id: str | None = None) -> Iterable[Report]:
        stmt = select(ReportModel)
        if user_id is not None:
            stmt = stmt.where(ReportModel.user_id == user_id)
        if work_type_id is not None:
            stmt = stmt.where(ReportModel.work_type_id == work_type_id)

        result = self._session.execute(stmt.order_by(ReportModel.created_at.desc()))
        models: List[ReportModel] = list(result.scalars().all())
        return [self._to_entity(model) for model in models]

    async def next_id(self) -> str:
        return uuid.uuid4().hex

    @staticmethod
    def _to_entity(model: ReportModel) -> Report:
        return Report(
            id=model.id,
            user_id=model.user_id,
            work_type_id=model.work_type_id,
            description=model.description,
            people=model.people,
            volume=model.volume,
            machines=model.machines,
            created_at=model.created_at,
            photo_urls=list(model.photo_urls or []),
        )
