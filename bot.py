"""Backward-compatible entry point for the Telegram bot."""

from __future__ import annotations

import asyncio

from app.bot.telegram import main, start_bot

__all__ = ["start_bot", "main"]


if __name__ == "__main__":
    asyncio.run(main())
