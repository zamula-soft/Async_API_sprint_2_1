from typing import Optional, Union
from abc import ABC, abstractmethod
from functools import lru_cache

from aioredis import Redis
from backoff import on_exception, expo
from fastapi import Depends

from db import get_redis
from models import Film, Person, Genre

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class AsyncCacheStorage(ABC):

    name_model = ''
    model = None

    @abstractmethod
    async def get_from_cache(self, **kwargs):
        pass

    @abstractmethod
    async def set_to_cache(self, **kwargs):
        pass


class RedisCache(AsyncCacheStorage):
    """Work with cache from Redis"""

    def __init__(self, redis: Redis, name_model, model):
        """Init."""
        self.redis = redis
        self.name_model = name_model
        self.model = model

    async def get_from_cache(self, item_id: str, **kwargs) -> Optional[Union[Film, Person, Genre]]:
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

    async def set_to_cache(self, item: Union[Film, Person, Genre]) -> None:
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


@lru_cache()
def get_redis_storage_service_movies(
        redis: Redis = Depends(get_redis),
) -> RedisCache:
    return RedisCache(redis, name_model='movies', model=Film)


@lru_cache()
def get_redis_storage_service_persons(
        redis: Redis = Depends(get_redis),
) -> RedisCache:
    return RedisCache(redis, name_model='persons', model=Person)


@lru_cache()
def get_redis_storage_service_genres(
        redis: Redis = Depends(get_redis),
) -> RedisCache:
    return RedisCache(redis, name_model='genres', model=Genre)


@lru_cache()
def get_redis_storage_service(
        redis: Redis = Depends(get_redis),
) -> RedisCache:
    return RedisCache(redis, name_model='genres', model=Genre)