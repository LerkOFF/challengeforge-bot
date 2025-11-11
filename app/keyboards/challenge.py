from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.callbacks import encode_vote, encode_save, encode_new, encode_noop

def challenge_keyboard(challenge_id: int, score: int) -> InlineKeyboardMarkup:
    row1 = [
        InlineKeyboardButton(text="👍", callback_data=encode_vote(challenge_id, 1)),
        InlineKeyboardButton(text=f"{score:+d}", callback_data=encode_noop()),
        InlineKeyboardButton(text="👎", callback_data=encode_vote(challenge_id, -1)),
    ]
    row2 = [
        InlineKeyboardButton(text="💾 Сохранить", callback_data=encode_save(challenge_id)),
        InlineKeyboardButton(text="🎲 Ещё", callback_data=encode_new()),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])
