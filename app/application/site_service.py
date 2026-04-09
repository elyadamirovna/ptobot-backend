"""Application service for site access based on user role."""
from __future__ import annotations

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
