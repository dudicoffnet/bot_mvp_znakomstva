import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN env is missing")

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# Главное меню
menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.row(types.KeyboardButton("🔍 Найти рядом"))
menu.row(types.KeyboardButton("📝 Моя анкета"))
menu.row(types.KeyboardButton("⚙️ Настройки"), types.KeyboardButton("💖 Помочь проекту"))

@dp.message_handler(commands=["start", "menu"])
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в бот «Сейчас»!", reply_markup=menu)

@dp.message_handler()
async def echo_menu(message: types.Message):
    if message.text in ["🔍 Найти рядом", "📝 Моя анкета", "⚙️ Настройки", "💖 Помочь проекту"]:
        await message.answer(f"Раздел «{message.text}» в разработке.")
    else:
        await message.answer("Используй кнопки меню ниже.", reply_markup=menu)

if __name__ == "__main__":
    print("Start polling...")
    executor.start_polling(dp, skip_updates=True)
