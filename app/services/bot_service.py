"""Telegram bot lifecycle management."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Optional

from bot import start_bot

logger = logging.getLogger(__name__)


class BotService:
    """Запускает и останавливает Telegram-бота."""

    def __init__(self, bot_token: Optional[str]) -> None:
        self._bot_token = bot_token
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if not self._bot_token:
            logger.warning("BOT_TOKEN is not set, Telegram bot will not be started")
            return
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(start_bot(self._bot_token))

    async def stop(self) -> None:
        if not self._task:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
