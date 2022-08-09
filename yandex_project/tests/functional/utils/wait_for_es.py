from backoff import on_exception, expo
from elasticsearch import Elasticsearch

from functional.core.settings import TestSettings

settings = TestSettings()


@on_exception(expo, BaseException)
def wait_for_es():
    es = Elasticsearch([f'http://{settings.elastic_host}:{settings.elastic_port}'], verify_certs=True)
    ping = es.ping()
    if ping:
        print('elastic work')
        return ping
    raise Exception
