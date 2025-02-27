import inspect
import logging
import logging.handlers
import sys

from loguru import logger

from app.env_settings import BASE_DIR


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logging(level: str) -> None:
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger.remove()
    handler = logging.handlers.SysLogHandler(address=("localhost", 514))
    logger.add(handler)
    logger.add(sys.stderr, level=level.upper())
    logger.add(BASE_DIR / "logs" / "tg.log", level=level.upper(), retention=5, rotation="5 MB")
