"""SQLAlchemy-based repository for reports."""
from __future__ import annotations

import uuid
from datetime import date
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Report, ReportHistoryItem, ReportWorkItem
from app.domain.ports import ReportRepository
from app.infrastructure.reports.models import ReportModel, ReportWorkItemModel
from app.infrastructure.users.models import UserModel
from app.infrastructure.work_types.models import WorkTypeModel


class SqlAlchemyReportRepository(ReportRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    async def add(self, report: Report) -> Report:
        model = ReportModel(
            id=report.id,
            user_id=report.user_id,
            site_id=report.site_id,
            work_type_id=report.work_type_id,
            report_date=report.report_date,
            description=report.description,
            people=report.people,
            volume=report.volume,
            machines=report.machines,
            created_at=report.created_at,
            photo_urls=list(report.photo_urls),
        )
        model.work_items = self._build_work_item_models(report)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    async def list(
        self,
        *,
        site_id: str | None = None,
        user_id: str | None = None,
        work_type_id: str | None = None,
    ) -> Iterable[Report]:
        stmt = select(ReportModel)
        if site_id is not None:
            stmt = stmt.where(ReportModel.site_id == site_id)
        if user_id is not None:
            stmt = stmt.where(ReportModel.user_id == user_id)
        if work_type_id is not None:
            stmt = stmt.outerjoin(ReportWorkItemModel, ReportWorkItemModel.report_id == ReportModel.id).where(
                (ReportModel.work_type_id == work_type_id) | (ReportWorkItemModel.work_type_id == work_type_id)
            )

        result = self._session.execute(stmt.order_by(ReportModel.created_at.desc())).unique()
        models: List[ReportModel] = list(result.scalars().all())
        return [self._to_entity(model) for model in models]

    async def list_history_by_site(
        self,
        *,
        site_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
        work_type_id: str | None = None,
        limit: int | None = None,
    ) -> Iterable[ReportHistoryItem]:
        stmt = (
            select(
                ReportModel,
                WorkTypeModel.name.label("work_type_name"),
                UserModel.name.label("author_name"),
            )
            .join(WorkTypeModel, WorkTypeModel.id == ReportModel.work_type_id)
            .join(UserModel, UserModel.id == ReportModel.user_id)
            .where(ReportModel.site_id == site_id)
        )

        if date_from is not None:
            stmt = stmt.where(ReportModel.report_date >= date.fromisoformat(date_from))
        if date_to is not None:
            stmt = stmt.where(ReportModel.report_date <= date.fromisoformat(date_to))
        if work_type_id is not None:
            stmt = stmt.outerjoin(ReportWorkItemModel, ReportWorkItemModel.report_id == ReportModel.id).where(
                (ReportModel.work_type_id == work_type_id) | (ReportWorkItemModel.work_type_id == work_type_id)
            )

        stmt = stmt.order_by(ReportModel.report_date.desc(), ReportModel.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit)

        rows = self._session.execute(stmt).unique().all()
        return [self._to_history_item(row) for row in rows]

    async def next_id(self) -> str:
        return uuid.uuid4().hex

    async def get_by_id(self, report_id: str) -> Report | None:
        model = self._session.get(ReportModel, report_id)
        return self._to_entity(model) if model else None

    async def update(self, report: Report) -> Report:
        model = self._session.get(ReportModel, report.id)
        if model is None:
            raise ValueError(f"Report {report.id} not found")

        model.user_id = report.user_id
        model.site_id = report.site_id
        model.work_type_id = report.work_type_id
        model.report_date = report.report_date
        model.description = report.description
        model.people = report.people
        model.volume = report.volume
        model.machines = report.machines
        model.created_at = report.created_at
        model.photo_urls = list(report.photo_urls)
        model.work_items = self._build_work_item_models(report)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, report_id: str) -> bool:
        model = self._session.get(ReportModel, report_id)
        if model is None:
            return False

        self._session.delete(model)
        self._session.commit()
        return True

    @staticmethod
    def _to_entity(model: ReportModel) -> Report:
        work_items = SqlAlchemyReportRepository._to_work_items(model)
        return Report(
            id=model.id,
            user_id=model.user_id,
            site_id=model.site_id or "",
            work_type_id=model.work_type_id,
            report_date=model.report_date,
            description=model.description,
            people=model.people,
            volume=model.volume,
            machines=model.machines,
            created_at=model.created_at,
            photo_urls=list(model.photo_urls or []),
            work_items=work_items,
        )

    @staticmethod
    def _to_history_item(row) -> ReportHistoryItem:
        model: ReportModel = row[0]
        work_type_name: str = row[1]
        author_name: str = row[2]
        work_items = SqlAlchemyReportRepository._to_work_items(model, fallback_name=work_type_name)
        return ReportHistoryItem(
            id=model.id,
            site_id=model.site_id or "",
            work_type_id=model.work_type_id,
            work_type_name=work_type_name,
            report_date=model.report_date,
            created_at=model.created_at,
            description=model.description,
            people=model.people,
            volume=model.volume,
            machines=model.machines,
            photo_urls=list(model.photo_urls or []),
            author_id=model.user_id,
            author_name=author_name,
            work_items=work_items,
        )

    @staticmethod
    def _to_work_items(model: ReportModel, fallback_name: str = "") -> List[ReportWorkItem]:
        if model.work_items:
            return [
                ReportWorkItem(
                    id=item.id,
                    work_type_id=item.work_type_id,
                    work_type_name=fallback_name if item.work_type_id == model.work_type_id else "",
                    description=item.description,
                    people=item.people,
                    volume=item.volume,
                    machines=item.machines,
                    sort_order=item.sort_order,
                )
                for item in model.work_items
            ]

        return [
            ReportWorkItem(
                id=f"{model.id}-legacy",
                work_type_id=model.work_type_id,
                work_type_name=fallback_name,
                description=model.description,
                people=model.people,
                volume=model.volume,
                machines=model.machines,
                sort_order=0,
            )
        ]

    @staticmethod
    def _build_work_item_models(report: Report) -> List[ReportWorkItemModel]:
        items = report.work_items or [
            ReportWorkItem(
                id=f"{report.id}-legacy",
                work_type_id=report.work_type_id,
                description=report.description,
                people=report.people,
                volume=report.volume,
                machines=report.machines,
                sort_order=0,
            )
        ]
        return [
            ReportWorkItemModel(
                id=item.id or uuid.uuid4().hex,
                report_id=report.id,
                work_type_id=item.work_type_id or report.work_type_id,
                description=item.description,
                people=item.people,
                volume=item.volume,
                machines=item.machines,
                sort_order=item.sort_order,
            )
            for item in items
        ]
