import asyncio
from loguru import logger

from app.logger_config import setup_logging
from app.config import Config
from app.bot import create_bot
from app.handlers.base import router as base_router


async def main():
    setup_logging()

    Config.validate()
    logger.info("Конфигурация загружена ✅")

    bot, dp = create_bot()
    dp.include_router(base_router)

    logger.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
