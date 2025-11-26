"""Root endpoint router."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
@router.head("/")
def health_check() -> dict[str, str]:
    """Простой health-check для корневого URL."""

    return {"status": "ok"}
