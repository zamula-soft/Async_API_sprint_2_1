import os

from pydantic import BaseSettings


class PostgresDsl(BaseSettings):

    dbname: str = os.environ.get('DB_NAME','movies_database')
    user: str = os.environ.get('DB_USER','app')
    password: str = os.environ.get('DB_PASSWORD','123qwe')
    host: str = os.environ.get('DB_HOST', '127.0.0.1')
    port: int = int(os.environ.get('DB_PORT', 5432))


class ElascticSearchDsl(BaseSettings):

    host: str = os.environ.get('ES_HOST', '127.0.0.1')
    port: int = int(os.environ.get('ES_PORT', 9200))


PACK_SIZE = int(os.environ.get('PACK_SIZE', 200))

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
