from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from app.storage.db import Database
from app.storage.repositories.challenge_repo import ChallengeRepo
from app.storage.repositories.vote_repo import VoteRepo
from app.services.rendering import render_challenge
from app.keyboards.challenge import challenge_keyboard

router = Router()

@router.inline_query()
async def inline_handler(iq: InlineQuery, db: Database):
    query = (iq.query or "").strip()

    # формат "cid:123" — показать конкретный челлендж
    cid = None
    if query.startswith("cid:"):
        try:
            cid = int(query.split(":", 1)[1])
        except ValueError:
            cid = None

    crepo = ChallengeRepo(db)
    vrepo = VoteRepo(db)

    results = []

    async def build_result(row):
        cid, title, body, tags = row
        score = await vrepo.get_score(cid)
        text = render_challenge(cid, title, body, tags, score)
        return InlineQueryResultArticle(
            id=str(cid),
            title=f"Челлендж #{cid}",
            description=title[:96],
            input_message_content=InputTextMessageContent(message_text=text, parse_mode="HTML"),
            reply_markup=challenge_keyboard(cid, score),
        )

    if cid:
        row = await crepo.get_by_id(cid)
        if row:
            results.append(await build_result(row))

    # если не задан cid, отдаём несколько последних/топовых для выбора
    if not results:
        top = await crepo.get_top_by_score(limit=5)
        # get_top_by_score возвращает (cid, title, score) — дотянем тело
        for cid, title, _ in top:
            full = await crepo.get_by_id(cid)
            if full:
                results.append(await build_result(full))

    await iq.answer(results=results, is_personal=False, cache_time=5)
