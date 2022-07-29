import sqlite3
from contextlib import contextmanager
from collections.abc import Generator

import psycopg2
from psycopg2 import OperationalError, extras
from psycopg2.extensions import connection as _connection


def dict_factory(curs: sqlite3.Cursor, row: tuple) -> dict:
    d = dict()

    for idx, col in enumerate(curs.description):
        d[col[0]] = row[idx]

    return d


@contextmanager
def sqlite_connector(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    try:
        yield conn
    except sqlite3.Error as exc:
        raise exc
    finally:
        conn.close()


@contextmanager
def postgres_connector(dsn: dict[str, str]) -> Generator[_connection, None, None]:
    conn = psycopg2.connect(**dsn, cursor_factory=psycopg2.extras.RealDictCursor)
    print(conn)
    try:
        yield conn
    except OperationalError as exc:
        print(exc)
        raise exc
    finally:
        conn.close()

