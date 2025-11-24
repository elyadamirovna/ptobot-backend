"""Telegram bot launcher."""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from dotenv import load_dotenv


load_dotenv()

WEBAPP_URL = os.getenv("WEBAPP_URL", "https://reports-frontend.onrender.com")


def _get_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""

    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable '{name}' is required for the Telegram bot."
        )
    return value


def _build_dispatcher(webapp_url: str) -> Dispatcher:
    """Configure the dispatcher with the start command handler."""

    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_cmd(message: types.Message) -> None:  # pragma: no cover - Telegram runtime
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Открыть отчёты",
                        web_app=WebAppInfo(url=webapp_url),
                    )
                ]
            ],
            resize_keyboard=True,
        )

        await message.answer(
            "Привет! Нажми кнопку, чтобы открыть приложение отчётов 👇",
            reply_markup=keyboard,
        )

    return dp


async def start_bot(bot_token: Optional[str] = None, webapp_url: Optional[str] = None) -> None:
    """Start the Telegram bot via long polling."""

    token = bot_token or _get_env("BOT_TOKEN")
    url = webapp_url or WEBAPP_URL

    bot = Bot(token=token)
    dp = _build_dispatcher(url)

    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main() -> None:
    """Standalone entry point used when running `python -m app.bot.telegram`."""

    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
