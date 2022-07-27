from backoff import on_exception, expo
import psycopg2
from psycopg2.extras import DictCursor

from settings import PACK_SIZE, PostgresDsl
from utils import logger
from postgres_d.queries import (
    QUERY_GET_GENRES,
    QUERY_GET_FILMS,
    QUERY_GET_PERSONS,
)


class PGLoader:
    """Load data from postgres"""

    def __init__(self) -> None:
        """Init."""
        self.pack_size = PACK_SIZE
        self.queries = {
            'movies':
                {
                    'query_get_data': QUERY_GET_FILMS,
                },
            'genres':
                {
                    'query_get_data': QUERY_GET_GENRES
                },
            'persons':
                {
                    'query_get_data': QUERY_GET_PERSONS
                }
            }

    @on_exception(expo, BaseException)
    def get_from_database(self, mod_date: str, type_data: str):
        """
        Get new film from database.
        :param mod_date: Date last update.
        :return:
        """
        with psycopg2.connect(**PostgresDsl().dict()) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:

                logger.debug(f'start get data from postgres for {type_data}')

                query = self.queries.get(type_data)
                cur.execute(query['query_get_data'].format(date_modify=mod_date))

                while row := cur.fetchmany(self.pack_size):
                    yield row

