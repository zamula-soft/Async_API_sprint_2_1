import logging
from logging.handlers import RotatingFileHandler
import os

logger = logging.getLogger('sqllite_to_postgrees')
logger.setLevel(logging.INFO)

fh = RotatingFileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'logs.log'), maxBytes=5000000, backupCount=5)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
