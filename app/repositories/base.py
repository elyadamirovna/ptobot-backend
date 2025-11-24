"""Base repository abstractions."""

from __future__ import annotations

from typing import List, Protocol

from app.models.report import ReportOut
from app.models.work_type import WorkTypeOut


class WorkTypeRepositoryProtocol(Protocol):
    def list_work_types(self) -> List[WorkTypeOut]:
        ...


class ReportRepositoryProtocol(Protocol):
    def add_report(self, report: ReportOut) -> None:
        ...

    def list_reports(self) -> List[ReportOut]:
        ...
