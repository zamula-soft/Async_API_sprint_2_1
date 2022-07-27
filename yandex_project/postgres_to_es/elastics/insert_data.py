from elasticsearch import Elasticsearch, helpers
import backoff
from typing import Generator, Iterable
from psycopg2.extras import DictCursor

from models import Person, Genre
from settings import ElascticSearchDsl
from utils import logger
from elastics.mapping import MAPPING_FILMS, MAPPING_GENRES, MAPPING_PERSONS

FIELDS = [
    'id',
    'rating',
    # 'genre',
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
        self._generators = {
            'movies': generate_data,
            'genres': generate_genres,
            'persons': generate_people,
        }
        self._mapping = [
            {'type': 'movies', 'mapping': MAPPING_FILMS},
            {'type': 'genres', 'mapping': MAPPING_GENRES},
            {'type': 'persons', 'mapping': MAPPING_PERSONS},
        ]

    def save_data(self, data, type_data) -> None:
        """
        Save data in Elasticsearch.
        :param data: data for save.
        :return:
        """
        logger.debug('\nSave data to elastic')
        self.__check_connection()
        generator = self._generators.get(type_data)
        helpers.bulk(self.__client, generator(data))

    @backoff.on_exception(backoff.expo, BaseException)
    def __check_connection(self) -> None:
        if not self.__client.ping():
            raise ConnectionError

    def create_mapping_films(self):
        logger.debug('\nDelete mapping from elastic')
        self.__check_connection()
        for mapping in self._mapping:
            logger.debug('Update mapping for {type}'.format(**mapping))
            if self.__client.indices.exists(index=mapping['type']):
                self.__client.indices.delete(index=mapping['type'])
            self.__client.indices.create(index=mapping['type'], body=mapping['mapping'])


def generate_genres(genres: Iterable[Genre]) -> Generator[dict, None, None]:
    for genre in genres:
        logger.debug('обновили или добавили genre {0}'.format(genre['id']))
        yield {
            '_index': 'genres',
            '_id': genre['id'],
            'name': genre['name'],
            'id': genre['id']
        }


def generate_data(movies_list):
    persons_fields = ['actors', 'writers', 'directors', 'genres']
    for movie in movies_list:
        logger.debug('обновили или добавили movie {0}'.format(movie['id']))
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


def generate_people(persons):
    for pers in persons:
        logger.debug('обновили или добавили person: {id}'.format(id=pers['id']))
        yield {
            '_index': 'persons',
            '_id': pers['id'],
            'full_name': pers['full_name'],
            'id': pers['id'],
        }
