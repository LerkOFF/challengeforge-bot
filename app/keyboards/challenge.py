from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.callbacks import (
    encode_vote,
    encode_save,
    encode_new,
    encode_noop,
    encode_save_decision,   # важно: есть в callbacks.py
)

def challenge_keyboard(challenge_id: int, score: int) -> InlineKeyboardMarkup:
    """
    Основная клавиатура под карточкой челленджа:
    👍  [+score]  👎
    💾 Сохранить | 🎲 Ещё
    📤 Поделиться (открывает inline-режим с префиксом cid:<id>)
    """
    row1 = [
        InlineKeyboardButton(text="👍", callback_data=encode_vote(challenge_id, 1)),
        InlineKeyboardButton(text=f"{score:+d}", callback_data=encode_noop()),
        InlineKeyboardButton(text="👎", callback_data=encode_vote(challenge_id, -1)),
    ]
    row2 = [
        InlineKeyboardButton(text="💾 Сохранить", callback_data=encode_save(challenge_id)),
        InlineKeyboardButton(text="🎲 Ещё", callback_data=encode_new()),
    ]
    row3 = [
        InlineKeyboardButton(text="📤 Поделиться", switch_inline_query=f"cid:{challenge_id}")
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3])


def save_decision_keyboard(challenge_id: int) -> InlineKeyboardMarkup:
    """
    Вопрос «Добавить заметку?» после нажатия 💾
    """
    row = [
        InlineKeyboardButton(
            text="Да, добавить",
            callback_data=encode_save_decision(challenge_id, "y"),
        ),
        InlineKeyboardButton(
            text="Нет",
            callback_data=encode_save_decision(challenge_id, "n"),
        ),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row])
