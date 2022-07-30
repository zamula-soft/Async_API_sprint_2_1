import os
import csv
import sqlite3
import tempfile

from psycopg2 import DatabaseError, OperationalError
from psycopg2.extensions import connection

from db_connectors import sqlite_connector, postgres_connector
from data_classes import FilmWork, Genre, Person, GenreFilmWork, PersonFilmWork
from logger import logger

tables = {
    'genre': Genre,
    'person': Person,
    'film_work': FilmWork,
    'genre_film_work': GenreFilmWork,
    'person_film_work': PersonFilmWork
}

BATCH_SIZE = 5000

def postgres_save_data(conn: connection):
    cursor = conn.cursor()

    for table, data_class in tables.items():
        print(table, data_class.__slots__)
        fieldnames = list(data_class.__slots__)
        if 'created_at' in fieldnames:
            fieldnames[fieldnames.index('created_at')] = 'created'
        if 'updated_at' in fieldnames:
            fieldnames[fieldnames.index('updated_at')] = 'modified'

        fild_names_str = ', '.join(fieldnames)
        file_path = os.path.abspath(os.path.join(tempfile.gettempdir(), f'{table}.csv'))

        cursor.execute('TRUNCATE TABLE content.{table} CASCADE;'.format(table=table))

        sql = f'COPY content.{table} ({fild_names_str}) FROM STDIN DELIMITER \',\' QUOTE \'"\' CSV HEADER'
        print(sql)
        cursor.copy_expert(sql, open(file_path, 'r'))

    cursor.close()
    conn.commit()


def sqllite_load_data(conn: sqlite3.Connection):

    '''
    Здесь был такой комментарий, но я не был уверен, что я правильно его понял, поэтому я создал файл load_data_2.py:

    было бы неплохо здесь сделать генератор, который бы возвращал путь до файла после записи всех строк для
    одной таблицы, а при следующем вызове удалял файл. Чтобы не хранить на диске сразу все файлы - на больших
    бд будешь сильно перерасходывать диск
    '''

    cursor = conn.cursor()
    for table, data_class in tables.items():
        file_path = os.path.abspath(os.path.join(tempfile.gettempdir(), f'{table}.csv'))
        print(file_path)
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = data_class.__slots__
                writer = csv.DictWriter(f, fieldnames)
                writer.writeheader()
                cursor.execute('SELECT {columns} FROM {table}'.format(
                    columns=', '.join(fieldnames), table=table
                ))
                while data := cursor.fetchmany(size=BATCH_SIZE):
                    writer.writerows(data)
        except IOError as e:

            logger.exception(f"Can't handle with file: {e.filename}.\n")

    cursor.close()


def load_from_sqlite(sqlite_connection: sqlite3.Connection, postgres_connection: connection) -> None:
    """ Основной метод загрузки данных из SQLite в Postgres """
    print('here')
    sqllite_load_data(sqlite_connection)
    postgres_save_data(postgres_connection)


if __name__ == '__main__':
    logger.info('start work load data')
    dsn = {
        'dbname': 'movies_database',
        'user': 'app',
        'password': '123qwe',
        'host': 'postgres',
        'port': 5432,
        'options': '-c search_path=content'
    }

    print(dsn)

    try:
        with sqlite_connector('db.sqlite') as sqlite_conn, postgres_connector(dsn) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
    except (DatabaseError, OperationalError, sqlite3.Error, TypeError) as exc:
        print(exc)
        logger.exception(f"Can't handle with database.\n")
