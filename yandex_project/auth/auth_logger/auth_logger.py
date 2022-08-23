from logging import getLogger, DEBUG, StreamHandler, Formatter
from sys import stdout


def get_logger(name):
    logger = getLogger(name)
    logger.setLevel(DEBUG)
    handler = StreamHandler(stdout)
    handler.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
