import asyncio
from loguru import logger

from app.logger_config import setup_logging
from app.config import Config
from app.bot import create_bot
from app.handlers.base import router as base_router
from app.handlers.inline import router as inline_router
from app.handlers.challenge import router as challenge_router
from app.storage.db import Database
from app.middlewares.ratelimit import RateLimitMiddleware

async def main():
    setup_logging()
    Config.validate()

    db = Database(Config.DB_PATH)
    await db.connect()

    bot, dp = create_bot()
    dp["db"] = db

    dp.message.middleware(RateLimitMiddleware(window_sec=10, max_actions=5, kinds=("message",)))
    dp.callback_query.middleware(RateLimitMiddleware(window_sec=10, max_actions=8, kinds=("callback",)))

    dp.include_router(base_router)
    dp.include_router(challenge_router)
    dp.include_router(inline_router)

    logger.info("Бот запущен ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
