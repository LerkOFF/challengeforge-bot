from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.callbacks import encode_page, encode_noop

def pagination_keyboard(list_id: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⟨ Назад", callback_data=encode_page(list_id, page - 1)))
    else:
        buttons.append(InlineKeyboardButton(text=" ", callback_data=encode_noop()))

    buttons.append(InlineKeyboardButton(text=f"Стр. {page}/{total_pages}", callback_data=encode_noop()))

    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="Вперёд ⟩", callback_data=encode_page(list_id, page + 1)))
    else:
        buttons.append(InlineKeyboardButton(text=" ", callback_data=encode_noop()))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])
