from typing import Any

from redis import Redis
import backoff

from settings import RedisDsl


class Status:
    """Get and update status last update ElasticSearch from Redis."""

    def __init__(self) -> None:
        """Init."""
        redis_dsl = RedisDsl()
        self._redis_db = Redis(host=redis_dsl.host, port=redis_dsl.port)

    def disconnect(self) -> None:
        """Disconnect Redis."""
        self._redis_db.close()

    @backoff.on_exception(backoff.expo, BaseException, max_tries=5)
    def get_status(self, key) -> Any:
        """
        Get date from Redis.

        :param key: Key for get data.
        :return: Data.
        """
        value = self._redis_db.get(key)
        return float(value) if value else value

    @backoff.on_exception(backoff.expo, BaseException, max_tries=5)
    def set_status(self, key: str, value: Any) -> None:
        """
        Update data in Redis.

        :param key: Key for data.
        :param value: Value data.
        :return: None.
        """
        self._redis_db.set(key, value=value)
