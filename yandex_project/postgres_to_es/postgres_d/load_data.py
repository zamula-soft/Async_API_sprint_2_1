from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor
import backoff

from .queries import QUERY_TEMPLATE, QUERY_GET_ALL_FILMS, QUERY_GET_FILMS_BY_DATE_MODIFY
from settings import PostgresDsl, PACK_SIZE


class PGLoader:
    """Load data from postgres"""

    def __init__(self) -> None:
        """Init."""
        self.pack_size = PACK_SIZE

    @backoff.on_exception(backoff.expo, BaseException)
    def get_movies_from_database(self, mod_date: datetime):
        """
        Get new film from database.
        :param mod_date: Date last update.
        :return:
        """
        with psycopg2.connect(**PostgresDsl().dict()) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                new_films = self._get_film_changes(cur, mod_date)
                if new_films:
                    sql_query_templ = QUERY_TEMPLATE
                    for fw_ids in new_films:
                        sql_query = sql_query_templ.format(', '.join([f"'{i}'" for i in fw_ids]))
                        cur.execute(sql_query)
                        yield cur.fetchall()

    def _get_film_changes(self, cur, mod_date: datetime):
        """
        Get new film ids.
        :param cur: Cursor.
        :param mod_date: Date last update.
        :return:
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
