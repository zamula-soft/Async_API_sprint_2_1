from time import sleep
from postgres_d import PGLoader
from elastics import ESLoader
from redis_work import Status
from datetime import datetime
import time


def transfer_data():
    print('start')
    pg_loader = PGLoader()
    es_loader = ESLoader()
    status = Status()

    print(status, pg_loader, es_loader)

    mod_date = status.get_status('mod_date')

    print('mod_date', mod_date)

    mod_date = datetime.fromtimestamp(mod_date) if mod_date else None

    print(mod_date)

    new_date = time.time()

    print(new_date)

    print(pg_loader.get_movies_from_database(mod_date))

    for movies in pg_loader.get_movies_from_database(mod_date):
        print('jfdk', movies)
        es_loader.save_data(movies)

    status.set_status('mod_date', new_date)
    status.disconnect()


if __name__ == '__main__':

    while True:
        transfer_data()
        sleep(10)
