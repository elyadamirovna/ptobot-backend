"""Async-safe in-memory repositories for development and testing."""
from __future__ import annotations

import asyncio
import itertools
from collections import deque
from datetime import date
from typing import Deque, Iterable, List

from app.domain.entities import Report, ReportHistoryItem, WorkType
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

    async def list(
        self,
        *,
        site_id: str | None = None,
        user_id: str | None = None,
        work_type_id: str | None = None,
    ) -> Iterable[Report]:
        async with self._lock:
            reports: Iterable[Report] = list(self._reports)
        if site_id is not None:
            reports = [item for item in reports if item.site_id == site_id]
        if user_id is not None:
            reports = [item for item in reports if item.user_id == user_id]
        if work_type_id is not None:
            reports = [item for item in reports if item.work_type_id == work_type_id]
        return list(reports)

    async def list_history_by_site(
        self,
        *,
        site_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
        work_type_id: str | None = None,
        limit: int | None = None,
    ) -> Iterable[ReportHistoryItem]:
        reports = await self.list(site_id=site_id, work_type_id=work_type_id)
        filtered = list(reports)
        if date_from is not None:
            filtered = [item for item in filtered if item.report_date >= date.fromisoformat(date_from)]
        if date_to is not None:
            filtered = [item for item in filtered if item.report_date <= date.fromisoformat(date_to)]
        filtered.sort(key=lambda item: (item.report_date, item.created_at), reverse=True)
        if limit is not None:
            filtered = filtered[:limit]
        return [
            ReportHistoryItem(
                id=item.id,
                site_id=item.site_id,
                work_type_id=item.work_type_id,
                work_type_name="",
                report_date=item.report_date,
                created_at=item.created_at,
                description=item.description,
                people=item.people,
                volume=item.volume,
                machines=item.machines,
                photo_urls=list(item.photo_urls),
                author_id=item.user_id,
                author_name="",
                work_items=list(item.work_items),
            )
            for item in filtered
        ]

    async def get_by_id(self, report_id: str) -> Report | None:
        async with self._lock:
            for report in self._reports:
                if report.id == report_id:
                    return report
        return None

    async def update(self, report: Report) -> Report:
        async with self._lock:
            for index, current in enumerate(self._reports):
                if current.id == report.id:
                    self._reports[index] = report
                    return report
        raise ValueError(f"Report {report.id} not found")

    async def delete(self, report_id: str) -> bool:
        async with self._lock:
            for report in list(self._reports):
                if report.id == report_id:
                    self._reports.remove(report)
                    return True
        return False


class InMemoryWorkTypeRepository(WorkTypeRepository):
    def __init__(self) -> None:
        self._work_types: List[WorkType] = [
            WorkType(id="1", name="Земляные работы"),
            WorkType(id="2", name="Бетонирование"),
            WorkType(id="3", name="Монтаж конструкций"),
        ]

    async def list(self) -> Iterable[WorkType]:
        return list(self._work_types)
