"""Sanity check for Settings model initialization."""

from __future__ import annotations

import os

from app.config.settings import Settings


def main() -> None:
    os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/app")
    Settings()


if __name__ == "__main__":
    main()
