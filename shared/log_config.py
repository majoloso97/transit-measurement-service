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


def get_uvicorn_log_config():
    uvicorn_log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'access': {
                'fmt': '%(asctime)s | %(name)s | %(levelname)s: %(client_addr)s - "%(request_line)s" %(status_code)s'
            },
            'default': {
                'fmt': '%(asctime)s | %(name)s | %(levelname)s: %(message)s'
            }
        }
    }
    return uvicorn_log_config
