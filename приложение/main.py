
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
from приложение.database import init_db, save_user, find_matches, get_all_users

load_dotenv()
init_db()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

class ProfileForm(StatesGroup):
    name = State()
    goals = State()

def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔍 Найти собеседника"))
    kb.add(KeyboardButton("📝 Моя анкета"))
    kb.add(KeyboardButton("⚙️ Настройки"), KeyboardButton("💖 Помочь"))
    return kb

@dp.message_handler(commands=['start', 'menu'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это честный бот знакомств. Выбери, что хочешь сделать:", reply_markup=main_kb())

@dp.message_handler(lambda message: message.text == "📝 Моя анкета")
async def start_form(message: types.Message):
    await ProfileForm.name.set()
    await message.answer("Как тебя зовут?")

@dp.message_handler(state=ProfileForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text, goals=[])
    await ProfileForm.goals.set()
    await message.answer("Выбери до 3 целей общения:", reply_markup=goals_kb())

goal_options = ["💬 Поболтать", "🚶 Прогулка", "🛍️ Пошопиться", "🎮 Игры", "📚 Почитать вместе"]

def goals_kb(selected=None):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    selected = selected or []
    for goal in goal_options:
        prefix = "✅ " if goal in selected else ""
        kb.add(KeyboardButton(f"{prefix}{goal}"))
    kb.add(KeyboardButton("✅ Готово"))
    return kb

@dp.message_handler(state=ProfileForm.goals)
async def process_goals(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    goals = user_data.get("goals", [])
    text = message.text.replace("✅ ", "")
    if text == "✅ Готово":
        name = user_data.get("name")
        save_user(message.from_user.id, name, goals)
        await state.finish()
        await message.answer(f"Анкета сохранена ✅\nИмя: {name}\nЦели: {', '.join(goals)}", reply_markup=main_kb())
    elif text in goal_options:
        if text in goals:
            goals.remove(text)
        elif len(goals) < 3:
            goals.append(text)
        else:
            await message.answer("Можно выбрать не более 3 целей")
        await state.update_data(goals=goals)
        await message.answer("Выбери цели:", reply_markup=goals_kb(goals))

@dp.message_handler(lambda message: message.text == "🔍 Найти собеседника")
async def match_user(message: types.Message):
    users = get_all_users()
    my_data = next((u for u in users if u[0] == message.from_user.id), None)
    if not my_data:
        await message.answer("Сначала заполни анкету 💡")
        return
    _, _, my_goals_str = my_data
    my_goals = my_goals_str.split(",")
    matches = find_matches(my_goals)
    matches = [m for m in matches if m[0] != message.from_user.id]
    if matches:
        reply = "\n".join([f"{m[1]} — {', '.join(m[2])}" for m in matches])
        await message.answer(f"Вот кто тебе подойдёт по интересам:\n{reply}")
    else:
        await message.answer("Пока нет совпадений. Попробуй позже 🔄")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
