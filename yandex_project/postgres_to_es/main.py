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
    
    newest_genre_date = status.get_status('mod_date') or 1
    newest_genre_date = datetime.fromtimestamp(newest_genre_date) 
    for genre in pg_loader.all_genres_from_database(newest_genre_date):
        es_loader.save_genres(genre)
        
    status.set_status('newest_genre_date', new_date)
    status.set_status('mod_date', new_date)
    status.disconnect()


if __name__ == '__main__':
    while True:
        try:
            transfer_data()
            sleep(10)
        except Exception as ex:
            print(ex)