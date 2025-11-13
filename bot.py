import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

BOT_TOKEN = "8429029689:AAEQTPlzIS29X4nMozXLEnGPBl0uwQVOOVA"
WEBAPP_URL = "https://reports-frontend.onrender.com"  # ссылка Static Site с Render

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_cmd(message: types.Message):
        # создаём клавиатуру СРАЗУ с кнопкой
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Открыть отчёты",
                        web_app=WebAppInfo(url=WEBAPP_URL)
                    )
                ]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "Привет! Нажми кнопку, чтобы открыть приложение отчётов 👇",
            reply_markup=keyboard
        )

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

