"""Routes for construction sites."""
from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.api.deps import get_site_service
from app.api.schemas import SiteRead
from app.api.security import get_current_user
from app.application import SiteService
from app.domain.entities import User

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=List[SiteRead])
def list_sites(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SiteService, Depends(get_site_service)],
) -> List[SiteRead]:
    sites = service.list_sites_for_user(current_user)
    return [SiteRead.from_entity(site) for site in sites]
