from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor
import backoff

from postgres_d.queries import QUERY_TEMPLATE, QUERY_GET_ALL_FILMS, QUERY_GET_FILMS_BY_DATE_MODIFY
from postgres_d.ps_context_managers import pg_cursor, pg_connect
from settings import PostgresDsl, PACK_SIZE


class PGLoader:
    """Get data from database."""

    def __init__(self) -> None:
        """Init."""
        self.pack_size = PACK_SIZE

    @backoff.on_exception(backoff.expo, BaseException, max_tries=5)
    def get_movies_from_database(self, mod_date: datetime):
        """
        Get movies from database.

        :param mod_date: date last get data from database.
        :return: data with films.
        """
        connection_ps = self.__get_connection(**PostgresDsl().dict())
        with pg_connect(connection_ps) as conn, pg_cursor(conn) as cur:
            sql_query_templ = QUERY_TEMPLATE
            for fw_ids in self.__get_changes(cur, mod_date):
                sql_query = sql_query_templ.format(tuple(fw_ids))
                cur.execute(sql_query)
                yield cur.fetchall()

    @backoff.on_exception(backoff.expo, BaseException, max_tries=5)
    def __get_connection(self, **dsl: dict) -> psycopg2.connect():
        """
        Create connection to postgres database.

        :param dsl: data for connect to postgres
        :return: connection to postgres
        """
        return psycopg2.connect(**dsl, cursor_factory=DictCursor)

    @backoff.on_exception(backoff.expo, BaseException, max_tries=5)
    def __get_changes(self, cur: psycopg2.connect().cursor(), mod_date: datetime) -> list:
        """
        Method for get updates from database by last date modified.

        :param cur: Cursor postgres.
        :param mod_date: Date last update ElasticSearch.
        :return: last update films.
        """
        if mod_date is None:
            sql_query = QUERY_GET_ALL_FILMS
        else:
            sql_query = QUERY_GET_FILMS_BY_DATE_MODIFY.format(mod_date=mod_date)

        cur.execute(sql_query)

        fw_ids = []
        while True:
            fw_ids.clear()
            result = cur.fetchmany(self.pack_size)

            if not result:
                return []

            for row in result:
                fw_ids.append(row['id'])

            yield fw_ids
