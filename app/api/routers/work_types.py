"""Routes for work types."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_work_type_repository
from app.models.work_type import WorkTypeOut
from app.repositories.work_type_repo import WorkTypeRepository

router = APIRouter(prefix="/work_types", tags=["work types"])


@router.get("", response_model=List[WorkTypeOut])
async def list_work_types(
    repository: WorkTypeRepository = Depends(get_work_type_repository),
) -> List[WorkTypeOut]:
    return repository.list_work_types()
