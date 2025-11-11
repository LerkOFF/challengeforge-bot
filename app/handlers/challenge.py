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

router = Router()

# --- /challenge ---
@router.message(Command("challenge"))
async def challenge_cmd(message: Message, db: Database):
    # регистрируем пользователя на всякий случай (вдруг не делал /start)
    urepo = UserRepo(db)
    user_id = await urepo.get_or_create(
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

# --- Голосование: cf:v:<id>:<value> ---
@router.callback_query(F.data.startswith("cf:v:"))
async def vote_callback(cb: CallbackQuery, db: Database):
    try:
        _, _, cid_str, val_str = cb.data.split(":")
        cid = int(cid_str)
        val = int(val_str)
        if val not in (1, -1):
            await cb.answer("Некорректный голос")
            return
    except Exception:
        await cb.answer("Ошибка данных")
        return

    # юзер
    urepo = UserRepo(db)
    uid = await urepo.get_or_create(
        tg_id=cb.from_user.id,
        username=cb.from_user.username or "",
        first_name=cb.from_user.first_name or "",
    )

    vrepo = VoteRepo(db)
    prev = await vrepo.get_user_vote(uid, cid)

    # Логика:
    # 1) если второй раз жмут тот же палец — снимаем голос
    # 2) если палец другой — меняем значение
    if prev == val:
        await vrepo.delete_vote(uid, cid)
        action_text = "Голос снят"
    else:
        await vrepo.upsert_vote(uid, cid, val)
        action_text = "Голос принят" if prev is None else "Голос изменён"

    # Перерисовка карточки
    crepo = ChallengeRepo(db)
    row = await crepo.get_by_id(cid)
    if not row:
        await cb.answer("Челлендж не найден")
        return
    _, title, body, tags = row
    score = await vrepo.get_score(cid)

    try:
        await cb.message.edit_text(
            render_challenge(cid, title, body, tags, score),
            reply_markup=challenge_keyboard(cid, score),
        )
    except TelegramBadRequest as e:
        # Телеграм может вернуть "message is not modified", если сумма голосов не изменилась.
        if "message is not modified" not in str(e).lower():
            raise
        # ничего страшного — просто не обновляем текст

    await cb.answer(action_text)

# --- Сохранить: cf:s:<id> ---
@router.callback_query(F.data.startswith("cf:s:"))
async def save_callback(cb: CallbackQuery, db: Database):
    try:
        _, _, cid_str = cb.data.split(":")
        cid = int(cid_str)
    except Exception:
        await cb.answer("Ошибка данных", show_alert=False)
        return

    urepo = UserRepo(db)
    uid = await urepo.get_or_create(
        tg_id=cb.from_user.id,
        username=cb.from_user.username or "",
        first_name=cb.from_user.first_name or "",
    )
    srepo = SavedRepo(db)
    await srepo.save(uid, cid)

    await cb.answer("Сохранено ✅", show_alert=False)

# --- Новый: cf:new ---
@router.callback_query(F.data == "cf:new")
async def new_callback(cb: CallbackQuery, db: Database):
    crepo = ChallengeRepo(db)
    vrepo = VoteRepo(db)
    cid, title, body, tags = await ensure_challenge(crepo)
    score = await vrepo.get_score(cid)
    await cb.message.edit_text(
        render_challenge(cid, title, body, tags, score),
        reply_markup=challenge_keyboard(cid, score)
    )
    await cb.answer("Новый челлендж 🎲")

# --- /my ---
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

# --- /top ---
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

# --- no-op, чтобы средняя кнопка рейтинга была кликабельной без действий ---
@router.callback_query(F.data == "cf:noop")
async def noop(cb: CallbackQuery):
    await cb.answer()
