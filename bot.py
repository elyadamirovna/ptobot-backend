import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command

BOT_TOKEN = "8429029689:AAEQTPlzIS29X4nMozXLEnGPBl0uwQVOOVA"

# Пока укажем http://127.0.0.1:8000 – позже сюда "подвесим" React
WEBAPP_URL = "https://example.com"  # временно заглушка


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )
        webapp_button = types.KeyboardButton(
            text="Открыть отчёты",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
        keyboard.add(webapp_button)

        await message.answer(
            "Привет! Нажми кнопку, чтобы открыть WebApp 👇",
            reply_markup=keyboard
        )

    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
