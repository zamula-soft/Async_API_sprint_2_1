from typing import Optional, Union, Type

from aioredis import Redis
from models import Film, Person, Genre

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class Cache:

    def __init__(self, redis: Redis, name_model: str, model: Type[Union[Film, Person, Genre]]):
        self.redis = redis
        self.name_model = name_model
        self.model = model

    async def _from_cache(self, item_id: str) -> Optional[Union[Film, Person, Genre]]:
        """
        Get item from Redis.
        :param item_id: item id.
        :return: Model Item
        """
        item_id = f'api_cache::elastic::movies::{item_id}'
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
        item_id = f'api_cache::elastic::{self.name_model}::{item.id}'
        await self.redis.set(item_id, item.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)
