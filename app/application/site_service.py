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
        return self._repository.list_by_contractor(user.id)

    def get_site_for_user(self, *, site_id: str, user: User) -> Site:
        site = self._repository.get_by_id(site_id)
        if site is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Объект не найден",
            )

        if user.role == "admin":
            return site

        if site.contractor_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к выбранному объекту",
            )

        return site

    def create_site(self, *, user: User, name: str, address: str, contractor_id: str | None) -> Site:
        self._ensure_admin(user)
        site = Site(
            id=uuid4().hex,
            name=name.strip(),
            address=address.strip(),
            contractor_id=contractor_id,
        )
        return self._repository.create(site)

    def update_site(
        self,
        *,
        user: User,
        site_id: str,
        name: str,
        address: str,
        contractor_id: str | None,
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
                contractor_id=contractor_id,
                contractor_name=existing.contractor_name,
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
