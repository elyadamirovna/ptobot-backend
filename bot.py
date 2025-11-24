"""Standalone Telegram bot entrypoint."""

from __future__ import annotations

import asyncio

from app.services.bot_service import main as bot_main, start_bot

__all__ = ["start_bot"]


if __name__ == "__main__":
    asyncio.run(bot_main())
