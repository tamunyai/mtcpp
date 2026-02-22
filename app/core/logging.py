import logging
import sys

from loguru import logger

from app.core.config import settings

logger.remove()

# Console logging
logger.add(
    sys.stdout,
    level="DEBUG" if settings.DEBUG else "INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<bold>{message}</bold> "
        "<dim>({name}:{function}:{line})</dim>"
    ),
    colorize=True,
    enqueue=True,
)

# File logging
logger.add(
    settings.LOG_FILE,
    rotation="1 MB",
    retention="7 days",
    compression="zip",
    level="INFO",
    serialize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)


class InterceptHandler(logging.Handler):
    """
    Intercepts standard python logging (Uvicorn/FastAPI)
    and redirects it to Loguru.
    """

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        _logger = logging.getLogger(name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False


def get_logger():
    return logger
