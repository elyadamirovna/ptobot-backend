"""Application service for site access based on user role."""
from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from typing import Iterable

from app.domain.entities import Site, User
from app.domain.ports import SiteRepository


class SiteService:
    def __init__(self, repository: SiteRepository) -> None:
        self._repository = repository

    def list_sites_for_user(self, user: User) -> Iterable[Site]:
        if user.role == "admin":
            return self._repository.list_all()
        if user.role == "pto_engineer":
            return self._repository.list_by_pto_engineer(user.id)
        return self._repository.list_by_contractor(user.id)

    def get_site(self, site_id: str) -> Site:
        site = self._repository.get_by_id(site_id)
        if site is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Объект не найден",
            )
        return site

    def get_site_for_user(self, *, site_id: str, user: User) -> Site:
        site = self.get_site(site_id)
        if user.role == "admin":
            return site

        if user.role == "pto_engineer":
            if site.pto_engineer_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к выбранному объекту",
                )
            return site

        if site.contractor_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к выбранному объекту",
            )

        return site

    def create_site(
        self,
        *,
        user: User,
        name: str,
        address: str,
        customer_name: str | None,
        project_manager_name: str | None,
        pto_responsible_name: str | None,
        start_date,
        planned_end_date,
        budget_total: str | None,
        budget_spent: str | None,
        progress_percent: int | None,
        status_note: str | None,
        contractor_id: str | None,
        pto_engineer_id: str | None,
    ) -> Site:
        self._ensure_admin(user)
        site = Site(
            id=uuid4().hex,
            name=name.strip(),
            address=address.strip(),
            customer_name=customer_name.strip() if customer_name else None,
            project_manager_name=project_manager_name.strip() if project_manager_name else None,
            pto_responsible_name=pto_responsible_name.strip() if pto_responsible_name else None,
            start_date=start_date,
            planned_end_date=planned_end_date,
            budget_total=budget_total.strip() if budget_total else None,
            budget_spent=budget_spent.strip() if budget_spent else None,
            progress_percent=progress_percent,
            status_note=status_note.strip() if status_note else None,
            contractor_id=contractor_id,
            pto_engineer_id=pto_engineer_id,
        )
        return self._repository.create(site)

    def update_site(
        self,
        *,
        user: User,
        site_id: str,
        name: str,
        address: str,
        customer_name: str | None,
        project_manager_name: str | None,
        pto_responsible_name: str | None,
        start_date,
        planned_end_date,
        budget_total: str | None,
        budget_spent: str | None,
        progress_percent: int | None,
        status_note: str | None,
        contractor_id: str | None,
        pto_engineer_id: str | None,
    ) -> Site:
        self._ensure_admin(user)
        existing = self._repository.get_by_id(site_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Объект не найден",
            )

        updated = self._repository.update(
            Site(
                id=existing.id,
                name=name.strip(),
                address=address.strip(),
                customer_name=customer_name.strip() if customer_name else None,
                project_manager_name=project_manager_name.strip() if project_manager_name else None,
                pto_responsible_name=pto_responsible_name.strip() if pto_responsible_name else None,
                start_date=start_date,
                planned_end_date=planned_end_date,
                budget_total=budget_total.strip() if budget_total else None,
                budget_spent=budget_spent.strip() if budget_spent else None,
                progress_percent=progress_percent,
                status_note=status_note.strip() if status_note else None,
                contractor_id=contractor_id,
                contractor_name=existing.contractor_name,
                pto_engineer_id=pto_engineer_id,
                pto_engineer_name=existing.pto_engineer_name,
                last_report_date=existing.last_report_date,
                has_today_report=existing.has_today_report,
                status=existing.status,
            )
        )
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Объект не найден",
            )
        return updated

    def delete_site(self, *, user: User, site_id: str) -> None:
        self._ensure_admin(user)
        deleted = self._repository.delete(site_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Объект не найден",
            )

    @staticmethod
    def _ensure_admin(user: User) -> None:
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступно только администратору",
            )
