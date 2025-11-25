"""Routes for work types."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from app.api.deps import get_work_type_service
from app.api.schemas import WorkTypeRead
from app.application import WorkTypeService

router = APIRouter(prefix="/work_types", tags=["work types"])


@router.get("", response_model=List[WorkTypeRead])
async def list_work_types(
    service: WorkTypeService = Depends(get_work_type_service),
) -> List[WorkTypeRead]:
    work_types = await service.list_work_types()
    return [WorkTypeRead.from_entity(work_type) for work_type in work_types]
