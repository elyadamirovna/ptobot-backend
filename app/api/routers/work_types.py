"""Work types router."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_work_type_repo
from app.models.work_type import WorkType
from app.repositories.work_type_repo import WorkTypeRepository

router = APIRouter(prefix="/work_types", tags=["work_types"])


@router.get("", response_model=List[WorkType], name="get_work_types")
async def get_work_types(
    repo: WorkTypeRepository = Depends(get_work_type_repo),
) -> List[WorkType]:
    return list(repo.list())
