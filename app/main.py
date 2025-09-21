
import asyncio
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

class Form(StatesGroup):
    name = State()
    goals = State()

GOALS = ["💬 Поболтать", "🚶 Прогулка", "🛍️ Пошопиться", "🎮 Игры", "📚 Почитать вместе"]
user_data = {}

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Привет! Как тебя зовут?")

@router.message(Form.name)
async def name_input(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text, goals=[])
    await state.set_state(Form.goals)
    builder = ReplyKeyboardBuilder()
    for goal in GOALS:
        builder.add(KeyboardButton(text=goal))
    builder.add(KeyboardButton(text="✅ Готово"))
    await message.answer("Выбери до 3 целей:", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(Form.goals)
async def goals_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected = data.get("goals", [])
    text = message.text.replace("✅ ", "")
    if text == "✅ Готово":
        name = data["name"]
        user_data[message.from_user.id] = {"name": name, "goals": selected}
        await state.clear()
        await message.answer(f"<b>Анкета сохранена</b>\nИмя: {name}\nЦели: {', '.join(selected)}", reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True))
    elif text in GOALS:
        if text in selected:
            selected.remove(text)
        elif len(selected) < 3:
            selected.append(text)
        else:
            await message.answer("Можно выбрать не более 3 целей")
        await state.update_data(goals=selected)
        builder = ReplyKeyboardBuilder()
        for goal in GOALS:
            prefix = "✅ " if goal in selected else ""
            builder.add(KeyboardButton(text=prefix + goal))
        builder.add(KeyboardButton(text="✅ Готово"))
        await message.answer("Обновлённый выбор:", reply_markup=builder.as_markup(resize_keyboard=True))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
