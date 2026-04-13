"""Port definition for site persistence."""
from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from app.domain.entities.site import Site


@runtime_checkable
class SiteRepository(Protocol):
    def get_by_id(self, site_id: str) -> Site | None:
        ...

    def list_all(self) -> Iterable[Site]:
        ...

    def list_by_contractor(self, contractor_id: str) -> Iterable[Site]:
        ...

    def list_by_pto_engineer(self, pto_engineer_id: str) -> Iterable[Site]:
        ...

    def create(self, site: Site) -> Site:
        ...

    def update(self, site: Site) -> Site | None:
        ...

    def delete(self, site_id: str) -> bool:
        ...
