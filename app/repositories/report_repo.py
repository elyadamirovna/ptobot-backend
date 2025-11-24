"""In-memory report repository."""

from __future__ import annotations

from collections import deque
from itertools import count
from typing import Deque, Iterable

from app.models.report import Report
from app.repositories.base import ReportRepositoryBase


class ReportRepository(ReportRepositoryBase):
    """Хранит отчёты в памяти с ограничением по количеству."""

    def __init__(self, max_reports: int = 500) -> None:
        self._reports: Deque[Report] = deque(maxlen=max_reports)
        self._id_counter = count(1)

    def add(self, report: Report) -> None:
        self._reports.append(report)

    def list(self) -> Iterable[Report]:
        return list(self._reports)

    def next_id(self) -> int:
        return next(self._id_counter)
