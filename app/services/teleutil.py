from aiogram.exceptions import TelegramBadRequest

async def safe_edit_card(bot, cb, text, reply_markup):
    try:
        if cb.inline_message_id:
            await bot.edit_message_text(
                text=text,
                inline_message_id=cb.inline_message_id,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
        else:
            await cb.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise
