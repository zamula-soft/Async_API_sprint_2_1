from time import sleep
from datetime import datetime

from postgres_d import PGLoader
from elastics import ESLoader
from redis_work import Status


def transfer_data():
    """
    Main function for transfer data from postgres to elasticsearch
    :return:
    """
    pg_loader = PGLoader()
    es_loader = ESLoader()
    status = Status()

    mod_date = status.get_status('mod_date')
    mod_date = mod_date.decode('utf-8') if mod_date else '2020-01-01 00:00:00'
    new_date = f'{datetime.now()}'

    for movies in pg_loader.get_movies_from_database(mod_date):
        es_loader.save_movies(movies)

    status.set_status('mod_date', new_date)
    status.disconnect()


if __name__ == '__main__':

    while True:
        transfer_data()
        sleep(10)
