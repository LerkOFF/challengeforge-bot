from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.storage.db import Database
from app.storage.repositories.user_repo import UserRepo
from app.storage.repositories.challenge_repo import ChallengeRepo
from app.storage.repositories.vote_repo import VoteRepo
from app.storage.repositories.saved_repo import SavedRepo
from app.services.challenge_factory import ensure_challenge
from app.services.rendering import render_challenge
from app.keyboards.challenge import challenge_keyboard
from app.keyboards.callbacks import decode, VotePayload, SavePayload

router = Router()

@router.message(Command("challenge"))
async def challenge_cmd(message: Message, db: Database):
    urepo = UserRepo(db)
    await urepo.get_or_create(
        tg_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
    )

    crepo = ChallengeRepo(db)
    vrepo = VoteRepo(db)
    cid, title, body, tags = await ensure_challenge(crepo)
    score = await vrepo.get_score(cid)

    await message.answer(
        render_challenge(cid, title, body, tags, score),
        reply_markup=challenge_keyboard(cid, score)
    )

@router.callback_query(F.data.startswith("cf:"))
async def generic_callback(cb: CallbackQuery, db: Database):
    parsed = decode(cb.data)
    if not parsed:
        await cb.answer("Некорректные данные", show_alert=False)
        return

    kind = parsed["type"]

    if kind == "noop":
        await cb.answer()
        return

    # гарантируем пользователя
    urepo = UserRepo(db)
    uid = await urepo.get_or_create(
        tg_id=cb.from_user.id,
        username=cb.from_user.username or "",
        first_name=cb.from_user.first_name or "",
    )

    if kind == "vote":
        payload: VotePayload = parsed["data"]
        vrepo = VoteRepo(db)

        prev = await vrepo.get_user_vote(uid, payload.cid)
        if prev == payload.val:
            await vrepo.delete_vote(uid, payload.cid)
            action_text = "Голос снят"
        else:
            await vrepo.upsert_vote(uid, payload.cid, payload.val)
            action_text = "Голос принят" if prev is None else "Голос изменён"

        crepo = ChallengeRepo(db)
        row = await crepo.get_by_id(payload.cid)
        if not row:
            await cb.answer("Челлендж не найден")
            return
        _, title, body, tags = row
        score = await vrepo.get_score(payload.cid)

        try:
            await cb.message.edit_text(
                render_challenge(payload.cid, title, body, tags, score),
                reply_markup=challenge_keyboard(payload.cid, score)
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise

        await cb.answer(action_text)
        return

    if kind == "save":
        payload: SavePayload = parsed["data"]
        srepo = SavedRepo(db)
        await srepo.save(uid, payload.cid)
        await cb.answer("Сохранено ✅")
        return

    if kind == "new":
        crepo = ChallengeRepo(db)
        vrepo = VoteRepo(db)
        cid, title, body, tags = await ensure_challenge(crepo)
        score = await vrepo.get_score(cid)
        try:
            await cb.message.edit_text(
                render_challenge(cid, title, body, tags, score),
                reply_markup=challenge_keyboard(cid, score)
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise
        await cb.answer("Новый челлендж 🎲")
        return

    # для будущих типов (page и т.п.)
    await cb.answer("Неизвестное действие", show_alert=False)
