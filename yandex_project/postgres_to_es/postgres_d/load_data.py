from backoff import on_exception, expo
import psycopg2
from psycopg2.extras import DictCursor

from settings import PACK_SIZE, PostgresDsl
from utils import logger
from postgres_d.queries import (
    QUERY_GET_FILMS_BY_DATE_MODIFY,
    QUERY_GET_GENRES,
    QUERY_TEMPLATE,
    QUERY_GET_PERSONS_BY_DATE_MODIFY,
    QUERY_GET_GENRES_BY_DATE_MODIFY,
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
                    'query_by_date_modify': QUERY_GET_FILMS_BY_DATE_MODIFY,
                    'query_get_data': QUERY_TEMPLATE,
                },
            'genres':
                {
                    'query_by_date_modify': QUERY_GET_GENRES_BY_DATE_MODIFY,
                    'query_get_data': QUERY_GET_GENRES
                },
            'persons':
                {
                    'query_by_date_modify': QUERY_GET_PERSONS_BY_DATE_MODIFY,
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
                new_data = self._get_changes(cur, mod_date, query['query_by_date_modify'])
                if new_data:
                    logger.debug('find data for update')
                    sql_query_templ = query['query_get_data']
                    for fw_ids in new_data:
                        sql_query = sql_query_templ.format(
                            ', '.join([f"'{i}'" for i in fw_ids]))
                        cur.execute(sql_query)

                        yield cur.fetchall()

    def _get_changes(self, cur, mod_date: str, query: str):
        """
        Get new film ids.
        :param cur: Cursor.
        :param mod_date: Date last update.
        :return:
        """

        logger.debug('start find new data')

        sql_query = query.format(date_modify=mod_date)

        cur.execute(sql_query)

        ids = []
        while True:
            ids.clear()
            result = cur.fetchmany(self.pack_size)
            if not result:
                return []

            for row in result:
                ids.append(row['id'])

            yield ids
