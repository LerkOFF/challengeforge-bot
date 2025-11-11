from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from app.storage.db import Database
from app.storage.repositories.user_repo import UserRepo

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message, db: Database):
    # message.from_user гарантирован в командных апдейтах
    u = message.from_user
    repo = UserRepo(db)
    user_id = await repo.get_or_create(
        tg_id=u.id,
        username=u.username or "",
        first_name=u.first_name or "",
    )

    await message.answer(
        "Привет! 👋\n"
        "Ты зарегистрирован в системе ChallengeForge.\n"
        "Используй /challenge, чтобы получить первую задачу."
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
