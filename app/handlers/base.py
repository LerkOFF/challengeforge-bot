from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! 👋\n"
        "Это ChallengeForge — бот, который будет генерировать задачи для прокачки твоих навыков.\n"
        "Используй /challenge чтобы получить первую задачу."
    )


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start — начало\n"
        "/help — помощь\n"
        "/challenge — получить челлендж\n"
        "/my — список сохранённого\n"
        "/top — топ челленджей"
    )
