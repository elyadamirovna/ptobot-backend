"""Telegram bot launcher and lifecycle management."""
from __future__ import annotations

import contextlib
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from fastapi import FastAPI, HTTPException, Request

from app.config import Settings

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


class BotService:
    """Manages Telegram bot lifecycle for FastAPI startup/shutdown."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._bot: Optional[Bot] = None
        self._dispatcher: Optional[Dispatcher] = None

    def _build_webhook_url(self) -> str:
        base_url = str(self._settings.webapp_url).rstrip("/")
        return f"{base_url}{self._settings.webhook_path}"

    def _register_webhook_route(self, app: FastAPI) -> None:
        webhook_secret = self._settings.webhook_secret_token

        @app.post(self._settings.webhook_path)
        async def telegram_webhook(update: Update, request: Request) -> dict[str, bool]:
            if webhook_secret:
                secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if secret_header != webhook_secret:
                    raise HTTPException(status_code=403, detail="Invalid secret token")

            if not self._dispatcher or not self._bot:
                raise HTTPException(status_code=503, detail="Bot is not ready")

            await self._dispatcher.feed_update(self._bot, update)
            return {"ok": True}

    async def start(self, app: FastAPI) -> None:
        bot_token = self._settings.bot_token
        if not bot_token:
            logger.warning("BOT_TOKEN is not set, Telegram bot will not be started")
            return

        self._bot = Bot(token=bot_token)
        self._dispatcher = _build_dispatcher(str(self._settings.webapp_url))
        webhook_url = self._build_webhook_url()

        await self._bot.set_webhook(
            url=webhook_url,
            secret_token=self._settings.webhook_secret_token,
        )
        logger.info("Webhook set to %s", webhook_url)

        self._register_webhook_route(app)

    async def stop(self, app: FastAPI) -> None:  # noqa: ARG002 - part of FastAPI lifecycle
        if not self._bot:
            return

        with contextlib.suppress(Exception):
            await self._bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted")

        with contextlib.suppress(Exception):
            await self._bot.session.close()

        self._bot = None
        self._dispatcher = None
