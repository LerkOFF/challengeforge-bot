from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def challenge_keyboard(challenge_id: int, score: int) -> InlineKeyboardMarkup:
    row1 = [
        InlineKeyboardButton(text="👍", callback_data=f"cf:v:{challenge_id}:1"),
        InlineKeyboardButton(text=f"{score:+d}", callback_data="cf:noop"),
        InlineKeyboardButton(text="👎", callback_data=f"cf:v:{challenge_id}:-1"),
    ]
    row2 = [
        InlineKeyboardButton(text="💾 Сохранить", callback_data=f"cf:s:{challenge_id}"),
        InlineKeyboardButton(text="🎲 Ещё", callback_data="cf:new"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])
