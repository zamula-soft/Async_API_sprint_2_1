import logging.handlers
import logging
import pathlib
import os 


logging_level = os.environ.get('LOGGING_LEVEL', 'DEBUG')

def get_logger(name):

    logging.basicConfig(level=logging_level, filemode='w')
    
    logging.getLogger("elasticsearch").setLevel(logging.WARNING)

    cwd = pathlib.Path(__file__).parent.resolve()
    file = cwd/'etl.log'

    log_format = logging.Formatter(
        '%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s %(message)s')

    f_handler = logging.FileHandler(filename=str(file), mode='a', encoding='utf-8')
    f_handler.setLevel(logging_level)
    f_handler.setFormatter(log_format)

    logger = logging.getLogger(name)
    logger.addHandler(f_handler)

    return logger



