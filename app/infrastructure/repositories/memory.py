"""Async-safe in-memory repositories for development and testing."""
from __future__ import annotations

import asyncio
import itertools
from collections import deque
from typing import Deque, Iterable, List

from app.domain.entities import Report, WorkType
from app.domain.ports import ReportRepository, WorkTypeRepository


class InMemoryReportRepository(ReportRepository):
    def __init__(self, *, limit: int = 500) -> None:
        self._reports: Deque[Report] = deque(maxlen=limit)
        self._id_counter = itertools.count(1)
        self._lock = asyncio.Lock()

    async def add(self, report: Report) -> Report:
        async with self._lock:
            self._reports.append(report)
        return report

    async def next_id(self) -> str:
        async with self._lock:
            return str(next(self._id_counter))

    async def list(self, *, user_id: str | None = None, work_type_id: str | None = None) -> Iterable[Report]:
        async with self._lock:
            reports: Iterable[Report] = list(self._reports)
        if user_id is not None:
            reports = [item for item in reports if item.user_id == user_id]
        if work_type_id is not None:
            reports = [item for item in reports if item.work_type_id == work_type_id]
        return list(reports)


class InMemoryWorkTypeRepository(WorkTypeRepository):
    def __init__(self) -> None:
        self._work_types: List[WorkType] = [
            WorkType(id="1", name="Земляные работы"),
            WorkType(id="2", name="Бетонирование"),
            WorkType(id="3", name="Монтаж конструкций"),
        ]

    async def list(self) -> Iterable[WorkType]:
        return list(self._work_types)
