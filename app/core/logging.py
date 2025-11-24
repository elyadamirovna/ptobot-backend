"""Application logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO, log_format: Optional[str] = None) -> None:
    """Configure basic logging for the application."""

    logging.basicConfig(
        level=level,
        format=log_format or "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
