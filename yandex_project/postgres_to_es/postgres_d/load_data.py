from datetime import datetime
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
import backoff

from .queries import QUERY_TEMPLATE, QUERY_GET_ALL_FILMS, QUERY_GET_FILMS_BY_DATE_MODIFY
from settings import POSTGRES_DSL, PACK_SIZE


class PGLoader:

    def __init__(self) -> None:
        self.pack_size = PACK_SIZE

    def get_movies_from_database(self, mod_date: datetime):
        with self.__pg_connect() as conn, self.__pg_cursor(conn) as cur:
            sql_query_templ = QUERY_TEMPLATE
            for fw_ids in self.__get_changes(cur, mod_date):
                sql_query = sql_query_templ.format(tuple(fw_ids))
                cur.execute(sql_query)
                yield cur.fetchall()

    @contextmanager
    def __pg_connect(self):
        conn = self.__get_connection(**POSTGRES_DSL)
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def __pg_cursor(self, conn: _connection):
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    @backoff.on_exception(backoff.expo, BaseException)
    def __get_connection(self, **dsl):
        return psycopg2.connect(**dsl, cursor_factory=DictCursor)

    def __get_changes(self, cur, mod_date: datetime):

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
