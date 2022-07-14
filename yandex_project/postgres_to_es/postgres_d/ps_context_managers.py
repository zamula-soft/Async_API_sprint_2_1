from contextlib import contextmanager

from psycopg2.extensions import connection as _connection


@contextmanager
def pg_connect(conn: _connection):
    """Context manager for connection postgres."""
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def pg_cursor(conn: _connection):
    """Context manager for cursor postgres."""
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
