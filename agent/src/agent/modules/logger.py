import logging
import os
import sys

from logging.handlers import RotatingFileHandler


levels = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


def get_logger(name, level=None, stdout=False):
    logger = logging.getLogger(name)
    level = level or levels.get(os.environ.get('LOG_LEVEL'), logging.INFO)
    logger.setLevel(level)

    file_handler = RotatingFileHandler(os.environ.get('LOG_FILE_PATH', 'agent.log'), maxBytes=2000)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    if stdout:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

    return logger
