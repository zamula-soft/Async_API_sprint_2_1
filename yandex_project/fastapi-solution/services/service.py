from typing import Optional, Type, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from backoff import on_exception, expo

from models import Film, Person, Genre
from .cache import RedisCache, AsyncCacheStorage


class Service:
    """Service for get data from elasticsearch."""

    def __init__(self, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param elastic: connect to Elasticsearch
        """
        self.elastic = elastic

    @on_exception(expo, BaseException)
    async def check_elastic_connection(self) -> None:
        """Check work elastic."""
        if not self.elastic.ping():
            raise ConnectionError


class ServiceGetByID(Service):
    """Service for get item by id."""
    def __init__(
            self,
            cache_storage: AsyncCacheStorage,
            elastic: AsyncElasticsearch,
    ) -> None:
        """
        Init.
        :param redis: connect to Redis
        :param elastic: connect to Elasticsearch
        :param name_model: name model for redis
        :param model: Model
        """
        super(ServiceGetByID, self).__init__(elastic=elastic)
        # Это место мне не очень нравится, но я не знаю, как сделать лучше.
        self.cache_storage = cache_storage

    async def get(self, item_id: str) -> Optional[Union[Film, Person, Genre]]:
        """
        Get item by id.
        :param item_id: Item id.
        :return: Model
        """
        item = await self.cache_storage.get_from_cache(item_id=item_id)
        if not item:
            item = await self._get_from_elastic(item_id)
            if not item:
                return None
            await self.cache_storage.set_to_cache(item=item)
        return item

    async def _get_from_elastic(self, item_id: str) -> Optional[Union[Film, Person, Genre]]:
        """
        Get item from elasticsearch by item id.
        :param item_id: Item id.
        :return: Model.
        """
        await self.check_elastic_connection()

        try:
            doc = await self.elastic.get(self.cache_storage.name_model, item_id)
        except NotFoundError:
            return None
        return self.cache_storage.model(**doc['_source'])
