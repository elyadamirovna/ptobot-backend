"""Application service for site access based on user role."""
from __future__ import annotations

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
