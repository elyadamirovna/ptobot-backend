"""In-memory repository for reports."""

from __future__ import annotations

import itertools
from collections import deque
from typing import Deque, Iterable, List, Optional

from app.models.report import ReportOut
from app.repositories.base import ReportRepositoryProtocol


class ReportRepository(ReportRepositoryProtocol):
    """Stores reports in memory with a bounded queue."""

    def __init__(self, limit: int = 500) -> None:
        self._reports: Deque[ReportOut] = deque(maxlen=limit)
        self._id_counter = itertools.count(1)

    def add_report(self, report: ReportOut) -> None:
        self._reports.append(report)

    def next_id(self) -> int:
        return next(self._id_counter)

    def list_reports(self, *, user_id: Optional[str] = None, work_type_id: Optional[str] = None) -> List[ReportOut]:
        items: Iterable[ReportOut] = self._reports
        if user_id is not None:
            items = [item for item in items if item.user_id == user_id]
        if work_type_id is not None:
            items = [item for item in items if item.work_type_id == work_type_id]
        return list(items)
