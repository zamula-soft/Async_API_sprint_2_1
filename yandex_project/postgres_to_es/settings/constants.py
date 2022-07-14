import os
from pydantic import BaseSettings


class PostgresDsl(BaseSettings):

    dbname: str = os.environ.get('DB_NAME')
    user: str = os.environ.get('DB_USER')
    password: str = os.environ.get('DB_PASSWORD')
    host: str = os.environ.get('DB_HOST', '127.0.0.1')
    port: int = int(os.environ.get('DB_PORT', 5432))


class ElascticSearchDsl(BaseSettings):

    host: str = os.environ.get('ES_HOST', '127.0.0.1')
    port: int = int(os.environ.get('ES_PORT', 9200))


class RedisDsl(BaseSettings):
    host: str = os.environ.get('REDIS_HOST', '127.0.0.1')
    port: int = int(os.environ.get('REDIS_PORT', 6379))


PACK_SIZE = int(os.environ.get('PACK_SIZE', 200))
