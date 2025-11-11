import time
from collections import defaultdict, deque
from typing import Any, Callable, Awaitable, Dict, Deque, Tuple

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class RateLimitMiddleware(BaseMiddleware):
    """
    Простой rate-limit.
    - window_sec: длина окна в секундах
    - max_actions: максимум событий в окне
    - kinds: какие типы обрабатывать ("message", "callback")
    """
    def __init__(self, window_sec: int = 10, max_actions: int = 5, kinds: Tuple[str, ...] = ("message", "callback")):
        super().__init__()
        self.window_sec = window_sec
        self.max_actions = max_actions
        self.kinds = kinds

        # ключ: (kind, user_id) → дека из timestamps
        self._hist: Dict[Tuple[str, int], Deque[float]] = defaultdict(deque)

    async def __call__(self,
                       handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
                       event: Message | CallbackQuery,
                       data: Dict[str, Any]) -> Any:
        now = time.monotonic()

        if isinstance(event, Message) and "message" in self.kinds:
            user_id = event.from_user.id if event.from_user else 0
            kind = "message"
            if self._limited(kind, user_id, now):
                try:
                    await event.answer("Слишком часто. Подожди немного ⏳")
                except Exception:
                    pass
                return
            self._push(kind, user_id, now)

        elif isinstance(event, CallbackQuery) and "callback" in self.kinds:
            user_id = event.from_user.id if event.from_user else 0
            kind = "callback"
            if self._limited(kind, user_id, now):
                try:
                    await event.answer("Слишком часто. Подожди немного ⏳", show_alert=False)
                except Exception:
                    pass
                return
            self._push(kind, user_id, now)

        return await handler(event, data)

    def _push(self, kind: str, uid: int, now: float) -> None:
        dq = self._hist[(kind, uid)]
        dq.append(now)
        self._shrink(dq, now)

    def _limited(self, kind: str, uid: int, now: float) -> bool:
        dq = self._hist[(kind, uid)]
        self._shrink(dq, now)
        return len(dq) >= self.max_actions

    def _shrink(self, dq: Deque[float], now: float) -> None:
        # удаляем события старше окна
        limit = now - self.window_sec
        while dq and dq[0] < limit:
            dq.popleft()
