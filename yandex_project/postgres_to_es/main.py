from datetime import datetime, timezone
from time import sleep

from elastics import ESLoader
from postgres_d import PGLoader
from redis_work import Status
from utils import logger


def transfer_data():
    """
    Main function for transfer data from postgres to elasticsearch
    :return:
    """
    pg_loader = PGLoader()
    es_loader = ESLoader()
    status = Status()

    new_date = f'{datetime.now(timezone.utc)}'
    mod_date = status.get_status('mod_date')
    mod_date = mod_date.decode('utf-8') if mod_date else '2020-01-01 00:00:00'

    logger.debug(f'film_work datetime before update: {mod_date}\n'
                 f'film_work datetime after update: {new_date}')

    if mod_date == '2020-01-01 00:00:00':
        es_loader.create_mapping_films()

    for type_data in ['movies', 'genres', 'persons']:
        for data in pg_loader.get_from_database(mod_date, type_data):
            es_loader.save_data(data, type_data)

    status.set_status('mod_date', new_date)

    status.disconnect()


if __name__ == '__main__':

    logger.debug('\n\nStart work\n\n')

    while True:
        logger.debug('\n\n\nFind changes')
        transfer_data()
        sleep(10)
        