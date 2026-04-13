"""SQLAlchemy-based repository for sites."""
from __future__ import annotations

from datetime import date
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

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

    def create(self, site: Site) -> Site:
        model = SiteModel(
            id=site.id,
            name=site.name,
            address=site.address,
            contractor_id=site.contractor_id,
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
        model.contractor_id = site.contractor_id
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
        latest_report_subquery = (
            select(
                ReportModel.site_id.label("site_id"),
                func.max(ReportModel.report_date).label("last_report_date"),
            )
            .where(ReportModel.site_id.is_not(None))
            .group_by(ReportModel.site_id)
            .subquery()
        )

        return (
            select(
                SiteModel,
                UserModel.name.label("contractor_name"),
                latest_report_subquery.c.last_report_date,
            )
            .outerjoin(UserModel, SiteModel.contractor_id == UserModel.id)
            .outerjoin(latest_report_subquery, latest_report_subquery.c.site_id == SiteModel.id)
            .order_by(SiteModel.name.asc())
        )

    @staticmethod
    def _to_entity(row) -> Site:
        site_model: SiteModel = row[0]
        contractor_name: str | None = row[1]
        last_report_date: date | None = row[2]
        has_today_report = last_report_date == date.today() if last_report_date else False

        return Site(
            id=site_model.id,
            name=site_model.name,
            address=site_model.address,
            contractor_id=site_model.contractor_id,
            contractor_name=contractor_name,
            last_report_date=last_report_date,
            has_today_report=has_today_report,
            status="sent" if has_today_report else "missing",
        )
