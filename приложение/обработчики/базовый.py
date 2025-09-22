from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import os

router = Router()

# --- Настройки админа ---
# 1) Можно указать ADMIN_CHAT_ID через переменную окружения (число)
# 2) Или просто один раз написать /start с аккаунта @u_468345698 — бот сам запомнит чат как админский
ADMIN_CHAT_ID_ENV = os.getenv("ADMIN_CHAT_ID")
ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_ENV) if ADMIN_CHAT_ID_ENV and ADMIN_CHAT_ID_ENV.isdigit() else None
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "u_468345698")  # можно переопределить в Railway

# --- Клавиатуры ---
kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Записаться")],
        [KeyboardButton(text="💰 Цены")],
        [KeyboardButton(text="📲 Связаться с мастером")],
    ],
    resize_keyboard=True
)

kb_cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

# --- Анкета (FSM) ---
class Booking(StatesGroup):
    name = State()
    car = State()
    date = State()
    phone = State()

def is_admin_user(message: Message) -> bool:
    u = message.from_user
    return bool(u and u.username and u.username.lower() == ADMIN_USERNAME.lower())

async def notify_admin(bot, text: str, fallback_chat_id=None):
    target_chat_id = -1002076509155
    try:
        await bot.send_message(target_chat_id, text)
        return True
    except Exception:
        return False

@router.message(CommandStart())
async def cmd_start(m: Message):
    global ADMIN_CHAT_ID
    # Автоприсвоение админа по username при первом /start
    if not ADMIN_CHAT_ID and is_admin_user(m):
        ADMIN_CHAT_ID = m.chat.id
        await m.answer(f"ADMIN_CHAT_ID автоматически установлен: {ADMIN_CHAT_ID}")
    await m.bot.send_photo(
        chat_id=m.chat.id,
        photo=FSInputFile("приложение/static/start_banner.png"),
        caption="Добро пожаловать в бот Диагномерс! 🚘\n\nЯ сканирую — ИИ анализирует. Максимальный результат!"
    )
    await m.bot.send_message(
        m.chat.id,
        "Привет! Я онлайн на Railway ✅\n\nВыберите действие:",
        reply_markup=kb_main
    )

@router.message(Command("setadmin"))
async def set_admin(m: Message):
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = m.chat.id
    await m.answer(f"ADMIN_CHAT_ID установлен: {ADMIN_CHAT_ID}")

@router.message(F.text == "💰 Цены")
async def prices(m: Message):
    await m.answer(
        "Диагностика Mercedes — от 30 BYN",
        reply_markup=kb_main
    )

@router.message(F.text == "📲 Связаться с мастером")
async def contact(m: Message):
    await m.answer("Связаться с мастером: @u_468345698", reply_markup=kb_main)

# --- Запись: запуск анкеты ---
@router.message(F.text == "📅 Записаться")
async def start_booking(m: Message, state: FSMContext):
    await state.set_state(Booking.name)
    await m.answer("Как вас зовут?", reply_markup=kb_cancel)

@router.message(Booking.name, F.text)
async def booking_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text.strip())
    await state.set_state(Booking.car)
    await m.answer("Модель и год автомобиля? (например: W204, 2013)")

@router.message(Booking.car, F.text)
async def booking_car(m: Message, state: FSMContext):
    await state.update_data(car=m.text.strip())
    await state.set_state(Booking.date)
    await m.answer("Удобная дата/время? (например: завтра после 16:00)")

@router.message(Booking.date, F.text)
async def booking_date(m: Message, state: FSMContext):
    await state.update_data(date=m.text.strip())
    await state.set_state(Booking.phone)
    await m.answer("Телефон для связи (можно с Telegram username).")

@router.message(Booking.phone, F.text)
async def booking_phone(m: Message, state: FSMContext):
    await state.update_data(phone=m.text.strip())
    data = await state.get_data()
    await state.clear()

    msg = (
        "✅ Новая заявка на диагностику\n"
        f"Имя: {data['name']}\n"
        f"Авто: {data['car']}\n"
        f"Когда: {data['date']}\n"
        f"Контакт: {data['phone']}\n"
        f"От пользователя: @{m.from_user.username if m.from_user.username else m.from_user.id}"
    )
    await m.answer("Заявка принята! Мастер свяжется с вами для подтверждения.", reply_markup=kb_main)

    sent = await notify_admin(m.bot, msg)
    if not sent:
        # если не смогли отправить админу — подскажем, как закрепить
        await m.answer("Мастер пока не привязан. Зайдите с аккаунта мастера и нажмите /start (или /setadmin), чтобы привязать чат для заявок.")

# Отмена анкеты
@router.message(F.text.lower() == "❌ отмена")
@router.message(Command("cancel"))
async def cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Отменил. Возвращаюсь в меню.", reply_markup=kb_main)

# Эхо на прочие тексты
@router.message(F.text)
async def echo(m: Message):
    await m.answer(f"Эхо: {m.text}", reply_markup=kb_main)