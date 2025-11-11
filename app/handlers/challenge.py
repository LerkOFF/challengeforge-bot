from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.storage.db import Database
from app.storage.repositories.challenge_repo import ChallengeRepo
from app.services.challenge_factory import ensure_challenge

router = Router()


@router.message(Command("challenge"))
async def challenge_cmd(message: Message, db: Database):
    repo = ChallengeRepo(db)
    cid, title, body, tags = await ensure_challenge(repo)

    # Пока без inline-кнопок.
    text = (
        f"💡 <b>Челлендж #{cid}</b>\n"
        f"<b>{title}</b>\n\n"
        f"{body}\n\n"
        f"Теги: " + " ".join(f"#{t.strip()}" for t in tags.split(",") if t.strip())
    )
    await message.answer(text)
