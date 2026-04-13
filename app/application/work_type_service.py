"""Application service for work types."""
from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from typing import Iterable

from app.domain.entities import User
from app.domain.entities.work_type import WorkType
from app.domain.ports import WorkTypeRepository


class WorkTypeService:
    def __init__(self, repository: WorkTypeRepository) -> None:
        self._repository = repository

    async def list_work_types(self) -> Iterable[WorkType]:
        return await self._repository.list()

    async def create_work_type(self, *, user: User, name: str) -> WorkType:
        self._ensure_admin(user)
        return await self._repository.create(WorkType(id=uuid4().hex, name=name.strip()))

    async def update_work_type(self, *, user: User, work_type_id: str, name: str) -> WorkType:
        self._ensure_admin(user)
        updated = await self._repository.update(WorkType(id=work_type_id, name=name.strip()))
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вид работ не найден",
            )
        return updated

    async def delete_work_type(self, *, user: User, work_type_id: str) -> None:
        self._ensure_admin(user)
        deleted = await self._repository.delete(work_type_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вид работ не найден",
            )

    @staticmethod
    def _ensure_admin(user: User) -> None:
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступно только администратору",
            )
