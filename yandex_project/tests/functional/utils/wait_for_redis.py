from backoff import on_exception, expo
from redis import Redis

from functional.core.settings import TestSettings

settings = TestSettings()


@on_exception(expo, BaseException)
def wait_for_redis():
    client = Redis(settings.redis_host, int(settings.redis_port))

    ping = client.ping()

    if ping:
        return ping
    raise Exception
