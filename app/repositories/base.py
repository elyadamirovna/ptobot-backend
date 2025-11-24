"""Base repository abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from app.models.report import Report
from app.models.work_type import WorkType


class WorkTypeRepositoryBase(ABC):
    """Абстракция репозитория видов работ."""

    @abstractmethod
    def list(self) -> Iterable[WorkType]:
        raise NotImplementedError


class ReportRepositoryBase(ABC):
    """Абстракция репозитория отчётов."""

    @abstractmethod
    def add(self, report: Report) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> Iterable[Report]:
        raise NotImplementedError
