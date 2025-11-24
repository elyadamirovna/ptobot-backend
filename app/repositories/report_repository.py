"""In-memory repository for reports."""

from __future__ import annotations

import itertools
from collections import deque
from typing import Deque, Iterable, List, Optional

from app.models.schemas import ReportOut


class ReportRepository:
    """Stores reports in memory with optional filtering."""

    def __init__(self, max_reports: int):
        self._reports: Deque[ReportOut] = deque(maxlen=max_reports)
        self._id_counter = itertools.count(1)

    def next_id(self) -> int:
        return next(self._id_counter)

    def save(self, report: ReportOut) -> ReportOut:
        self._reports.append(report)
        return report

    def list(self, user_id: Optional[str] = None, work_type_id: Optional[str] = None) -> List[ReportOut]:
        def matches(report: ReportOut) -> bool:
            if user_id is not None and report.user_id != user_id:
                return False
            if work_type_id is not None and report.work_type_id != work_type_id:
                return False
            return True

        filtered: Iterable[ReportOut] = filter(matches, self._reports)
        return list(filtered)
