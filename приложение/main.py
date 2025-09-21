
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Router
from aiogram.enums import ParseMode

from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Состояния анкеты ---
class ProfileForm(StatesGroup):
    name = State()
    goals = State()

# --- Хранилище временное (потом SQLite) ---
users = {}

# --- Главное меню ---
def main_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Найти собеседника")],
            [KeyboardButton(text="📝 Моя анкета")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="💖 Помочь")],
        ], resize_keyboard=True
    )
    return kb

@router.message(F.text.in_(["/start", "/menu"]))
async def cmd_start(m: Message):
    await m.answer("Добро пожаловать! ☀️\n\nЗдесь можно познакомиться по общим интересам — честно, без оценок.", reply_markup=main_kb())

@router.message(F.text == "📝 Моя анкета")
async def start_form(m: Message, state: FSMContext):
    await m.answer("Как тебя зовут?")
    await state.set_state(ProfileForm.name)

@router.message(ProfileForm.name)
async def process_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text, goals=[])
    await m.answer("Выбери до 3 целей общения:", reply_markup=goals_kb())
    await state.set_state(ProfileForm.goals)

# --- Выбор целей ---
goal_options = ["💬 Поболтать", "🚶 Прогулка", "🛍️ Пошопиться", "🎮 Игры", "📚 Почитать вместе"]

def goals_kb(selected=None):
    kb = ReplyKeyboardBuilder()
    selected = selected or []
    for goal in goal_options:
        prefix = "✅ " if goal in selected else "" 
        kb.button(text=f"{prefix}{goal}")
    kb.button(text="✅ Готово")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

@router.message(ProfileForm.goals)
async def process_goals(m: Message, state: FSMContext):
    data = await state.get_data()
    text = m.text.replace("✅ ", "")
    goals = data.get("goals", [])
    if text == "✅ Готово":
        name = data.get("name")
        users[m.from_user.id] = {"name": name, "goals": goals}
        await state.clear()
        await m.answer(f"Анкета сохранена ✅\nИмя: {name}\nЦели: {', '.join(goals)}", reply_markup=main_kb())
    elif text in goal_options:
        if text in goals:
            goals.remove(text)
        elif len(goals) < 3:
            goals.append(text)
        else:
            await m.answer("Можно выбрать не более 3 целей")
        await state.update_data(goals=goals)
        await m.answer("Выбери цели:", reply_markup=goals_kb(goals))
