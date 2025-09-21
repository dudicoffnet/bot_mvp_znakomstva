
from aiogram import Dispatcher, types

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def send_welcome(message: types.Message):
        await message.answer("Привет! Это тестовый бот знакомств.")
