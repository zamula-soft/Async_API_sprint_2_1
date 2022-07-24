from typing import Any

from redis import Redis

from settings import REDIS_PORT, REDIS_HOST


class Status:
    """Get last update elasticsearch"""

    def __init__(self) -> None:
        """Init."""
        self._redis_db = Redis(host=REDIS_HOST, port=REDIS_PORT)

    def disconnect(self) -> None:
        """Close connection."""
        self._redis_db.close()

    def get_status(self, key) -> Any:
        """
        Get current status.
        :param key: key.
        :return: last update.
        """
        return self._redis_db.get(key)

    def set_status(self, key: str, value: Any) -> None:
        """
        Update status.
        :param key:
        :param value:
        :return:
        """
        self._redis_db.set(key, value=value)
