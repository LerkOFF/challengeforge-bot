from aiogram.fsm.state import StatesGroup, State

class SaveNote(StatesGroup):
    waiting_note = State()  # ждём текст заметки после подтверждения
