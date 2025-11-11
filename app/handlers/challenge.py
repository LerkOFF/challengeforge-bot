from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from app.states.user_state import SaveNote
from app.storage.db import Database
from app.storage.repositories.user_repo import UserRepo
from app.storage.repositories.challenge_repo import ChallengeRepo
from app.storage.repositories.vote_repo import VoteRepo
from app.storage.repositories.saved_repo import SavedRepo
from app.services.challenge_factory import ensure_challenge
from app.services.rendering import render_challenge
from app.services.teleutil import safe_edit_card
from app.keyboards.challenge import challenge_keyboard, save_decision_keyboard
from app.keyboards.callbacks import (
    decode,
    VotePayload,
    SavePayload,
    SaveNoteDecisionPayload,
)

router = Router()

MAX_NOTE_LEN = 500


# /challenge — выдать карточку
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
        reply_markup=challenge_keyboard(cid, score),
    )


# /my — список сохранённого (первые 10)
@router.message(Command("my"))
async def my_cmd(message: Message, db: Database):
    urepo = UserRepo(db)
    uid = await urepo.get_or_create(
        tg_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
    )
    srepo = SavedRepo(db)
    rows = await srepo.list_for_user(uid, limit=10)
    if not rows:
        await message.answer("Пока пусто. Сохраняй интересные челленджи кнопкой 💾")
        return

    lines = [f"📚 Твои сохранённые (первые {len(rows)}):"]
    for cid, title, score in rows:
        lines.append(f"• #{cid} {title}  ({score:+d})")
    await message.answer("\n".join(lines))


# /top — топ по сумме голосов (первые 10)
@router.message(Command("top"))
async def top_cmd(message: Message, db: Database):
    crepo = ChallengeRepo(db)
    rows = await crepo.get_top_by_score(limit=10)
    if not rows:
        await message.answer("Пока нет челленджей.")
        return
    lines = ["🏆 Топ челленджей:"]
    for cid, title, score in rows:
        lines.append(f"• #{cid} {title}  ({score:+d})")
    await message.answer("\n".join(lines))


# /cancel — выйти из состояния FSM
@router.message(Command("cancel"))
async def cancel_cmd(message: Message, state: FSMContext):
    cur = await state.get_state()
    if cur is None:
        await message.answer("Нет активного действия.")
        return
    await state.clear()
    await message.answer("Отменено.")


# Универсальный обработчик всех callback'ов нашего протокола cf:...
@router.callback_query(F.data.startswith("cf:"))
async def generic_callback(cb: CallbackQuery, db: Database, state: FSMContext):
    parsed = decode(cb.data)
    if not parsed:
        await cb.answer("Некорректные данные", show_alert=False)
        return

    kind = parsed["type"]

    # no-op централизованно
    if kind == "noop":
        await cb.answer()
        return

    # Гарантируем пользователя
    urepo = UserRepo(db)
    uid = await urepo.get_or_create(
        tg_id=cb.from_user.id,
        username=cb.from_user.username or "",
        first_name=cb.from_user.first_name or "",
    )

    # --- Голосование ---
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

        await safe_edit_card(
            cb.bot,
            cb,
            render_challenge(payload.cid, title, body, tags, score),
            challenge_keyboard(payload.cid, score),
        )
        await cb.answer(action_text)
        return

    # --- Нажали «Сохранить» ---
    if kind == "save":
        payload: SavePayload = parsed["data"]
        await cb.message.reply(
            f"Добавить заметку к челленджу #{payload.cid}?",
            reply_markup=save_decision_keyboard(payload.cid),
        )
        await cb.answer()
        return

    # --- Решение по заметке (Да/Нет) ---
    if kind == "save_decision":
        payload: SaveNoteDecisionPayload = parsed["data"]
        srepo = SavedRepo(db)

        if payload.decision == "n":
            await srepo.save(uid, payload.cid)
            await cb.answer("Сохранено без заметки ✅")
            # Попробуем убрать клавиатуру у сообщения-вопроса
            try:
                if cb.inline_message_id:
                    await cb.bot.edit_message_reply_markup(
                        inline_message_id=cb.inline_message_id, reply_markup=None
                    )
                else:
                    await cb.message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest:
                pass
            return

        if payload.decision == "y":
            # Включаем FSM и ждём текст заметки
            await state.set_state(SaveNote.waiting_note)
            await state.update_data(challenge_id=payload.cid)
            # Меняем текст сообщения-вопроса на инструкцию
            await safe_edit_card(
                cb.bot,
                cb,
                f"Напиши заметку для челленджа #{payload.cid} (до {MAX_NOTE_LEN} символов).\n"
                f"Чтобы отменить — /cancel",
                None,
            )
            await cb.answer()
            return

        await cb.answer("Некорректное решение", show_alert=False)
        return

    # --- Новый челлендж ---
    if kind == "new":
        crepo = ChallengeRepo(db)
        vrepo = VoteRepo(db)
        cid, title, body, tags = await ensure_challenge(crepo)
        score = await vrepo.get_score(cid)
        await safe_edit_card(
            cb.bot,
            cb,
            render_challenge(cid, title, body, tags, score),
            challenge_keyboard(cid, score),
        )
        await cb.answer("Новый челлендж 🎲")
        return

    # Для будущих типов (например, пагинации)
    await cb.answer("Неизвестное действие", show_alert=False)


# При активном состоянии ждём текст заметки
@router.message(SaveNote.waiting_note)
async def save_note_receive(message: Message, db: Database, state: FSMContext):
    data = await state.get_data()
    cid = data.get("challenge_id")
    note = (message.text or "").strip()

    if not cid:
        await state.clear()
        await message.answer("Что-то пошло не так. Попробуй ещё раз.")
        return

    if not note:
        await message.answer("Заметка пустая. Напиши текст или /cancel")
        return

    if len(note) > MAX_NOTE_LEN:
        await message.answer(f"Слишком длинно. Максимум {MAX_NOTE_LEN} символов.")
        return

    urepo = UserRepo(db)
    uid = await urepo.get_or_create(
        tg_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
    )
    srepo = SavedRepo(db)
    await srepo.save_with_note(uid, cid, note)

    await state.clear()
    await message.answer("Сохранено с заметкой ✅")
