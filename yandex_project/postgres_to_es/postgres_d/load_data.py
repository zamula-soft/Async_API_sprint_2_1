import typing
from datetime import datetime

import backoff
import psycopg2
from psycopg2.extras import DictCursor
from settings import PACK_SIZE, PostgresDsl
from models import Person

from .queries import (QUERY_GET_ALL_FILMS, QUERY_GET_FILMS_BY_DATE_MODIFY, QUERY_GET_NEW_GENRES,
                      QUERY_TEMPLATE)


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
                        sql_query = sql_query_templ.format(
                            ', '.join([f"'{i}'" for i in fw_ids]))
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
            sql_query = QUERY_GET_FILMS_BY_DATE_MODIFY.format(
                mod_date=mod_date)

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

    def get_new_persons(self, newest_person_date: str) -> typing.Generator[Person, None, None] | None:
        """
        Достает person, обновленные после newest_person_date
        """
        with psycopg2.connect(**PostgresDsl().dict()) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute('SELECT * FROM content.person where modified > %s ORDER BY modified desc;',
                            (newest_person_date,))
                while row := cur.fetchone():
                    yield Person(**dict(row))

    def get_new_genres(self, newest_genre_date: datetime) -> typing.Generator[Person, None, None] | None:
        """
        Достает genre, обновленные после newest_genre_date
        """
        with psycopg2.connect(**PostgresDsl().dict()) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(QUERY_GET_NEW_GENRES, (newest_genre_date,))
                yield cur.fetchall()
