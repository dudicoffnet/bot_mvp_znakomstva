
from aiogram import Bot, Dispatcher, executor, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import register_handlers

import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token="YOUR_BOT_TOKEN_HERE",
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(bot)

register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
