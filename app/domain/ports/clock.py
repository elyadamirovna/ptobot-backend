"""Clock abstraction for deterministic time management."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    def now(self) -> datetime:
        ...


class UtcClock:
    """UTC-based clock implementation."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
