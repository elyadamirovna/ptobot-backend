"""Telegram bot launcher and lifecycle management."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from fastapi import FastAPI

from app.core.config import Settings

logger = logging.getLogger(__name__)


def _build_dispatcher(webapp_url: str) -> Dispatcher:
    """Configure the dispatcher with the start command handler."""

    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_cmd(message: types.Message) -> None:  # pragma: no cover - Telegram runtime
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Открыть отчёты", web_app=WebAppInfo(url=webapp_url))]],
            resize_keyboard=True,
        )

        await message.answer(
            "Привет! Нажми кнопку, чтобы открыть приложение отчётов 👇",
            reply_markup=keyboard,
        )

    return dp


async def start_bot(bot_token: str, webapp_url: str) -> None:
    """Start the Telegram bot via long polling."""

    bot = Bot(token=bot_token)
    dp = _build_dispatcher(webapp_url)

    logger.info("Starting Telegram bot")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Telegram bot stopped")


class BotService:
    """Manages Telegram bot lifecycle for FastAPI startup/shutdown."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._task_attr = "bot_task"

    async def start(self, app: FastAPI) -> None:
        bot_token = self._settings.bot_token
        if not bot_token:
            logger.warning("BOT_TOKEN is not set, Telegram bot will not be started")
            setattr(app.state, self._task_attr, None)
            return

        task = asyncio.create_task(start_bot(bot_token, self._settings.webapp_url))
        setattr(app.state, self._task_attr, task)

    async def stop(self, app: FastAPI) -> None:
        bot_task: Optional[asyncio.Task] = getattr(app.state, self._task_attr, None)
        if not bot_task:
            return

        bot_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await bot_task


async def main() -> None:
    settings = Settings()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required to start the bot")

    await start_bot(settings.bot_token, settings.webapp_url)


if __name__ == "__main__":
    asyncio.run(main())
