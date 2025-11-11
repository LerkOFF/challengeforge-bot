from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    waiting_note = State()  # Тут будем ждать заметку от пользователя при сохранении челленджа
