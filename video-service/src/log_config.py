import logging
from settings import settings


def setup_logger(logger: logging.Logger, remove_handlers: bool = False):
    template = '%(asctime)s | %(name)s | %(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt=template)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setFormatter(formatter)

    log_level = logging.getLevelName(settings.LOG_LEVEL)

    if remove_handlers:
        logger.handlers.clear()

    logger.setLevel(log_level)
    logger.addHandler(terminal_handler)
