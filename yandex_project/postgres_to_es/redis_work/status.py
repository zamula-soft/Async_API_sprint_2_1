from typing import Any

from redis import Redis

from settings import REDIS_PORT, REDIS_HOST


class Status:

    def __init__(self) -> None:
        self._redis_db = Redis(host=REDIS_HOST, port=REDIS_PORT)

    def disconnect(self) -> None:
        self._redis_db.close()

    def get_status(self, key) -> Any:
        value = self._redis_db.get(key)
        return float(value) if value else value

    def set_status(self, key: str, value: Any) -> None:
        self._redis_db.set(key, value=value)
