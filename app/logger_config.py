from loguru import logger
import sys


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <cyan>{level}</cyan> | {message}"
    )

    return logger
