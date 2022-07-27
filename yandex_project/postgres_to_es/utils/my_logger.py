from logging import basicConfig, getLogger, FileHandler, WARNING, Formatter
from pathlib import Path
from os import environ


logging_level = environ.get('LOGGING_LEVEL', 'DEBUG')


def get_logger(name):

    basicConfig(level=logging_level, filemode='w')
    
    getLogger("elasticsearch").setLevel(WARNING)

    cwd = Path(__file__).parent.resolve()
    file = cwd/'etl.log'

    log_format = Formatter(
        '%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s %(message)s')

    f_handler = FileHandler(filename=str(file), mode='a', encoding='utf-8')
    f_handler.setLevel(logging_level)
    f_handler.setFormatter(log_format)

    my_logger = getLogger(name)
    my_logger.addHandler(f_handler)

    return my_logger


logger = get_logger(__name__)



