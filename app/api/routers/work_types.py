"""Routes for work types."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_work_type_service
from app.api.schemas import WorkTypeRead, WorkTypeWrite
from app.api.security import get_current_user
from app.application import WorkTypeService
from app.domain.entities import User

router = APIRouter(prefix="/work_types", tags=["work types"])


@router.get("", response_model=List[WorkTypeRead])
async def list_work_types(
    service: WorkTypeService = Depends(get_work_type_service),
) -> List[WorkTypeRead]:
    work_types = await service.list_work_types()
    return [WorkTypeRead.from_entity(work_type) for work_type in work_types]


@router.post("", response_model=WorkTypeRead, status_code=status.HTTP_201_CREATED)
async def create_work_type(
    body: WorkTypeWrite,
    current_user: User = Depends(get_current_user),
    service: WorkTypeService = Depends(get_work_type_service),
) -> WorkTypeRead:
    work_type = await service.create_work_type(
        user=current_user,
        name=body.name,
        parent_id=body.parent_id,
        sort_order=body.sort_order,
        unit=body.unit,
        is_active=body.is_active,
        requires_volume=body.requires_volume,
        requires_people=body.requires_people,
        requires_machines=body.requires_machines,
    )
    return WorkTypeRead.from_entity(work_type)


@router.patch("/{work_type_id}", response_model=WorkTypeRead)
async def update_work_type(
    work_type_id: str,
    body: WorkTypeWrite,
    current_user: User = Depends(get_current_user),
    service: WorkTypeService = Depends(get_work_type_service),
) -> WorkTypeRead:
    work_type = await service.update_work_type(
        user=current_user,
        work_type_id=work_type_id,
        name=body.name,
        parent_id=body.parent_id,
        sort_order=body.sort_order,
        unit=body.unit,
        is_active=body.is_active,
        requires_volume=body.requires_volume,
        requires_people=body.requires_people,
        requires_machines=body.requires_machines,
    )
    return WorkTypeRead.from_entity(work_type)


@router.delete("/{work_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_type(
    work_type_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkTypeService = Depends(get_work_type_service),
) -> Response:
    await service.delete_work_type(user=current_user, work_type_id=work_type_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
