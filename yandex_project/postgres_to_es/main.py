from time import sleep
from postgres_d import PGLoader
from elastics import ESLoader
from redis_work import Status
from datetime import datetime
import time


def transfer_data():
    pg_loader = PGLoader()
    es_loader = ESLoader()
    status = Status()

    mod_date = status.get_status('mod_date')

    mod_date = datetime.fromtimestamp(mod_date) if mod_date else None

    new_date = time.time()

    for movies in pg_loader.get_movies_from_database(mod_date):
        es_loader.save_data(movies)

    status.set_status('mod_date', new_date)
    status.disconnect()


if __name__ == '__main__':

    while True:
        transfer_data()
        sleep(10)
