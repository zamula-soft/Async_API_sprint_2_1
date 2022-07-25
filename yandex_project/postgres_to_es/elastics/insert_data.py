from elasticsearch import Elasticsearch, helpers
import backoff
from typing import Generator, Iterable
from psycopg2.extras import DictCursor

from models import Person, Genre
from settings import ElascticSearchDsl
from utils import get_logger

logger = get_logger(__name__)

FIELDS = [
    'id',
    'rating',
    'genre',
    'title',
    'description',
    'directors_names',
    'actors_names',
    'writers_names',
    'writers',
    'actors',
    'directors',
    'genres',
]


class ESLoader:
    """Insert data to Elasticsearch."""

    def __init__(self) -> None:
        self.__client = Elasticsearch(hosts=[ElascticSearchDsl().dict()])

    def save_movies(self, data) -> None:
        """
        Save data in Elasticsearch.
        :param data: data for save.
        :return:
        """
        self.__check_connection()
        helpers.bulk(self.__client, generate_data(data))

    def save_persons(self, persons: Iterable[Person]) -> None:
        helpers.bulk(self.__client, generate_people(persons))

    @backoff.on_exception(backoff.expo, BaseException)
    def __check_connection(self) -> None:
        if not self.__client.ping():
            raise ConnectionError

    def save_genres(self, genres: Iterable[Genre]) -> None:
        helpers.bulk(self.__client, generate_genres(genres))


def generate_genres(genres: Iterable[DictCursor]) -> Generator[dict, None, None]:
    for genre in genres:
        logger.debug('обновили или добавили genre {0}'.format(genre['id']))
        yield {
            '_index': 'genres',
            '_id': genre['id'],
            'name': genre['name'],
        }


def generate_data(movies_list):
    persons_fields = ['actors', 'writers', 'directors', 'genres']
    for movie in movies_list:
        logger.debug('обновили или добавили movie', movie['id'])
        doc = {}
        for fld_name in FIELDS:
            if fld_name in persons_fields:
                doc[fld_name] = [{'id': person['id'], 'name': person['name']}
                                 for person in movie[fld_name]]
            elif fld_name == 'directors_names' and movie[fld_name] is None:
                doc[fld_name] = []
            else:
                doc[fld_name] = movie[fld_name]

        yield {
            '_index': 'movies',
            '_id': movie['id'],
            **doc,
        }


def generate_people(persons: Iterable[Person]):
    for pers in persons:
        logger.debug('обновили или добавили person: {0}, {1}'.format(pers.full_name, pers.id))
        yield {
            '_index': 'persons',
            '_id': pers.id,
            'full_name': pers.full_name
        }
