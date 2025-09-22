import os, sys, asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramUnauthorizedError
from .обработчики import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

async def preflight(bot: Bot):
    try:
        me = await bot.get_me()
        logging.info(f"✅ Bot OK: @{me.username} (id={me.id})")
    except TelegramUnauthorizedError:
        logging.error("❌ Неверный токен: Telegram вернул Unauthorized")
        sys.exit(1)

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token or ":" not in token:
        logging.error("❌ ENV BOT_TOKEN не задан или некорректен")
        sys.exit(1)

    bot = Bot(token=token)
    await preflight(bot)

    dp = Dispatcher()
    dp.include_router(router)

    logging.info("▶️ Старт поллинга…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    asyncio.run(main())