from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.callbacks import (
    encode_vote, encode_save, encode_new, encode_noop, encode_save_decision
)

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

def save_decision_keyboard(challenge_id: int) -> InlineKeyboardMarkup:
    row = [
        InlineKeyboardButton(text="Да, добавить", callback_data=encode_save_decision(challenge_id, "y")),
        InlineKeyboardButton(text="Нет", callback_data=encode_save_decision(challenge_id, "n")),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row])
