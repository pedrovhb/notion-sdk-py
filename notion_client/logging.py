import logging


def make_console_logger():
    logger = logging.getLogger(__package__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
