from typing import Optional, Union, Type

from aioredis import Redis
from backoff import on_exception, expo

from models import Film, Person, Genre

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class RedisCache:
    """Work with cache from Redis"""

    def __init__(self, redis: Redis, name_model: str, model: Type[Union[Film, Person, Genre]]):
        """Init."""
        self.redis = redis
        self.name_model = name_model
        self.model = model

    async def _from_cache(self, item_id: str) -> Optional[Union[Film, Person, Genre]]:
        """
        Get item from Redis.
        :param item_id: item id.
        :return: Model Item
        """
        await self.check_redis_connection()
        item_id = f'api_cache::elastic::{self.name_model}::{item_id}'
        data = await self.redis.get(item_id)
        if not data:
            return None

        return self.model.parse_raw(data)

    async def _put_to_cache(self, item: Union[Film, Person, Genre]) -> None:
        """
        Save item to Redis. Create cache.
        :param item: Model
        :return:
        """
        await self.check_redis_connection()
        item_id = f'api_cache::elastic::{self.name_model}::{item.id}'
        await self.redis.set(item_id, item.json(), expire=CACHE_EXPIRE_IN_SECONDS)

    @on_exception(expo, BaseException)
    async def check_redis_connection(self) -> None:
        """Check work redis."""
        if not self.redis.ping():
            raise ConnectionError
