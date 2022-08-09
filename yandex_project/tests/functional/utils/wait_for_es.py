from backoff import on_exception, expo
from elasticsearch import AsyncElasticsearch

from functional.core.settings import TestSettings

settings = TestSettings()


@on_exception(expo, BaseException)
def wait_for_es():
    client = AsyncElasticsearch(hosts=f"{settings.elastic_host}:{settings.elastic_port}")

    ping = client.ping()

    if ping:
        return ping
    raise Exception
