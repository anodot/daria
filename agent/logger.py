import config
import logging

from logging.handlers import RotatingFileHandler


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = RotatingFileHandler(config.log_file_path, maxBytes=2000)
    file_handler.setFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.addHandler(file_handler)
    return logger
