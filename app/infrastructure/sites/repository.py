"""SQLAlchemy-based repository for sites."""
from __future__ import annotations

from datetime import date
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.domain.entities import Site
from app.domain.ports import SiteRepository
from app.infrastructure.reports.models import ReportModel
from app.infrastructure.sites.models import SiteModel
from app.infrastructure.users.models import UserModel


class SqlAlchemySiteRepository(SiteRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, site_id: str) -> Site | None:
        stmt = self._base_stmt().where(SiteModel.id == site_id)
        row = self._session.execute(stmt).first()
        return self._to_entity(row) if row else None

    def list_all(self) -> Iterable[Site]:
        rows = self._session.execute(self._base_stmt()).all()
        return [self._to_entity(row) for row in rows]

    def list_by_contractor(self, contractor_id: str) -> Iterable[Site]:
        stmt = self._base_stmt().where(SiteModel.contractor_id == contractor_id)
        rows = self._session.execute(stmt).all()
        return [self._to_entity(row) for row in rows]

    def list_by_pto_engineer(self, pto_engineer_id: str) -> Iterable[Site]:
        stmt = self._base_stmt().where(SiteModel.pto_engineer_id == pto_engineer_id)
        rows = self._session.execute(stmt).all()
        return [self._to_entity(row) for row in rows]

    def create(self, site: Site) -> Site:
        model = SiteModel(
            id=site.id,
            name=site.name,
            address=site.address,
            customer_name=site.customer_name,
            project_manager_name=site.project_manager_name,
            pto_responsible_name=site.pto_responsible_name,
            start_date=site.start_date,
            planned_end_date=site.planned_end_date,
            budget_total=site.budget_total,
            budget_spent=site.budget_spent,
            progress_percent=site.progress_percent,
            status_note=site.status_note,
            contractor_id=site.contractor_id,
            pto_engineer_id=site.pto_engineer_id,
        )
        self._session.add(model)
        self._session.commit()
        return self.get_by_id(site.id) or site

    def update(self, site: Site) -> Site | None:
        model = self._session.get(SiteModel, site.id)
        if model is None:
            return None

        model.name = site.name
        model.address = site.address
        model.customer_name = site.customer_name
        model.project_manager_name = site.project_manager_name
        model.pto_responsible_name = site.pto_responsible_name
        model.start_date = site.start_date
        model.planned_end_date = site.planned_end_date
        model.budget_total = site.budget_total
        model.budget_spent = site.budget_spent
        model.progress_percent = site.progress_percent
        model.status_note = site.status_note
        model.contractor_id = site.contractor_id
        model.pto_engineer_id = site.pto_engineer_id
        self._session.commit()
        return self.get_by_id(site.id)

    def delete(self, site_id: str) -> bool:
        model = self._session.get(SiteModel, site_id)
        if model is None:
            return False

        self._session.delete(model)
        self._session.commit()
        return True

    @staticmethod
    def _base_stmt():
        contractor_user = aliased(UserModel)
        pto_engineer_user = aliased(UserModel)
        latest_report_subquery = (
            select(
                ReportModel.site_id.label("site_id"),
                func.max(ReportModel.report_date).label("last_report_date"),
            )
            .where(ReportModel.site_id.is_not(None))
            .group_by(ReportModel.site_id)
            .subquery()
        )
        recent_reports_subquery = (
            select(
                ReportModel.site_id.label("site_id"),
                ReportModel.report_date.label("report_date"),
                func.row_number()
                .over(
                    partition_by=ReportModel.site_id,
                    order_by=ReportModel.report_date.desc(),
                )
                .label("row_num"),
            )
            .where(ReportModel.site_id.is_not(None))
            .subquery()
        )
        recent_report_dates_subquery = (
            select(
                recent_reports_subquery.c.site_id,
                func.array_agg(recent_reports_subquery.c.report_date).label("recent_report_dates"),
            )
            .where(recent_reports_subquery.c.row_num <= 7)
            .group_by(recent_reports_subquery.c.site_id)
            .subquery()
        )

        return (
            select(
                SiteModel,
                contractor_user.name.label("contractor_name"),
                pto_engineer_user.name.label("pto_engineer_name"),
                latest_report_subquery.c.last_report_date,
                recent_report_dates_subquery.c.recent_report_dates,
            )
            .outerjoin(contractor_user, SiteModel.contractor_id == contractor_user.id)
            .outerjoin(pto_engineer_user, SiteModel.pto_engineer_id == pto_engineer_user.id)
            .outerjoin(latest_report_subquery, latest_report_subquery.c.site_id == SiteModel.id)
            .outerjoin(recent_report_dates_subquery, recent_report_dates_subquery.c.site_id == SiteModel.id)
            .order_by(SiteModel.name.asc())
        )

    @staticmethod
    def _to_entity(row) -> Site:
        site_model: SiteModel = row[0]
        contractor_name: str | None = row[1]
        pto_engineer_name: str | None = row[2]
        last_report_date: date | None = row[3]
        recent_report_dates: list[date] | None = row[4]
        has_today_report = last_report_date == date.today() if last_report_date else False

        return Site(
            id=site_model.id,
            name=site_model.name,
            address=site_model.address,
            customer_name=site_model.customer_name,
            project_manager_name=site_model.project_manager_name,
            pto_responsible_name=site_model.pto_responsible_name,
            start_date=site_model.start_date,
            planned_end_date=site_model.planned_end_date,
            budget_total=site_model.budget_total,
            budget_spent=site_model.budget_spent,
            progress_percent=site_model.progress_percent,
            status_note=site_model.status_note,
            contractor_id=site_model.contractor_id,
            contractor_name=contractor_name,
            pto_engineer_id=site_model.pto_engineer_id,
            pto_engineer_name=pto_engineer_name,
            last_report_date=last_report_date,
            recent_report_dates=list(recent_report_dates or []),
            has_today_report=has_today_report,
            status="sent" if has_today_report else "missing",
        )
