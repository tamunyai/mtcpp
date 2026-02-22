import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")


def get_logger():
    return logger
