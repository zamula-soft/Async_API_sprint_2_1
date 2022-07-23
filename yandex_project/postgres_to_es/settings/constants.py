import os

POSTGRES_DSL = {
    'dbname': os.environ.get('DB_NAME', 'movies_database'),
    'user': os.environ.get('DB_USER', 'app'),
    'password': os.environ.get('DB_PASSWORD', '123qwe'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', 5432)),
}

PACK_SIZE = int(os.environ.get('PACK_SIZE', 200))

ELASTICSEARCH_DSL = [
    {
        'host': os.environ.get('ES_HOST', '127.0.0.1'),
        'port': int(os.environ.get('ES_PORT', 9200)),
    }
]

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
