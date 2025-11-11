import asyncio
from loguru import logger

from app.bot import create_bot
from app.config import Config
from app.handlers.base import router as base_router


async def main():
    Config.validate()

    bot, dp = create_bot()

    # Подключаем маршруты
    dp.include_router(base_router)

    logger.info("✅ ChallengeForge bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
