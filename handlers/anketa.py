from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("myprofile"))
async def cmd_myprofile(message: Message):
    await message.answer("Анкета в разработке: имя → возраст → город → фото → цели.")
