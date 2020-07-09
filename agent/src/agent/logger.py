import logging
import os

from logging.handlers import RotatingFileHandler


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = RotatingFileHandler(os.environ.get('LOG_FILE_PATH', 'agent.log'), maxBytes=2000)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    test = 1
    return logger
