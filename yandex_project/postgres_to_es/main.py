from datetime import datetime
from time import sleep

from elastics import ESLoader
from postgres_d import PGLoader
from redis_work import Status
from utils import get_logger

logger = get_logger(__name__)


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
    new_date = f'{datetime.utcnow()}'# тут надо часовой пояс указывать, иначе рассинхрон пойдет
    logger.debug('film_work datetime before update : %s', mod_date)
    logger.debug('film_work datetime after update : %s', new_date)

    if mod_date == '2020-01-01 00:00:00':
        es_loader.create_mapping_films()

    for movies in pg_loader.get_movies_from_database(mod_date):
        es_loader.save_movies(movies)

    status.set_status('mod_date', new_date)

    # жанры сделал в твоем стиле
    last_genre_date = status.get_status('newest_genre_date')
    last_genre_date = last_genre_date.decode(
        'utf-8') if last_genre_date else '2000-01-01'
    logger.debug('last_genre_date : %s', last_genre_date)
    new_genre_date = f'{datetime.utcnow()}'
    status.set_status('newest_genre_date', new_genre_date)
    logger.debug('newest_genre_date after update : %s', new_genre_date)

    for genre in pg_loader.get_new_genres(last_genre_date):
        es_loader.save_genres(genre)

    # в персонах попробовал другой loader
    last_person_date = status.get_status('last_person_date')
    last_person_date = last_person_date.decode(
        'utf-8') if last_person_date else '2000-01-01'
    logger.debug('last_person_date :: %s', last_person_date)
    new_person_date = f'{datetime.utcnow()}'

    persons = pg_loader.get_new_persons(last_person_date)
    es_loader.save_persons(persons)
    logger.debug('last_person_date :: %s', last_person_date)
    status.set_status('last_person_date', new_person_date)

    status.disconnect()


if __name__ == '__main__':

    while True:
        logger.debug('ищем обновленные записи')
        transfer_data()
        sleep(10)
        