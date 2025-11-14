"""Telegram bot launcher."""

from __future__ import annotations

import asyncio
import os
from typing import Final

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from dotenv import load_dotenv


load_dotenv()


def _get_env(name: str) -> str:
    """Return a required environment variable or raise a clear error."""

    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable '{name}' is required for the Telegram bot."
        )
    return value


BOT_TOKEN: Final[str] = _get_env("BOT_TOKEN")
WEBAPP_URL: Final[str] = os.getenv(
    "WEBAPP_URL", "https://reports-frontend.onrender.com"
)


async def main() -> None:
    """Configure polling dispatcher and start the bot."""

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_cmd(message: types.Message) -> None:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Открыть отчёты",
                        web_app=WebAppInfo(url=WEBAPP_URL),
                    )
                ]
            ],
            resize_keyboard=True,
        )

        await message.answer(
            "Привет! Нажми кнопку, чтобы открыть приложение отчётов 👇",
            reply_markup=keyboard,
        )

    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

