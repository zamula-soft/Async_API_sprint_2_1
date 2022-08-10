from typing import Optional, Type, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from models import Film, Person, Genre
from .cache import Cache


class Service:
    """Service for get data from elasticsearch."""

    def __init__(self, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param elastic: connect to Elasticsearch
        """
        self.elastic = elastic


class ServiceGetByID(Service, Cache):

    def __init__(
            self,
            redis: Redis,
            elastic: AsyncElasticsearch,
            name_model: str,
            model: Type[Union[Film, Person, Genre]]
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
        self.redis = redis
        self.name_model = name_model
        self.model = model

    async def get(self, item_id: str) -> Optional[Union[Film, Person, Genre]]:
        """
        Get item by id.
        :param item_id: Item id.
        :return: Model
        """
        item = await self._from_cache(item_id)
        if not item:
            item = await self._get_from_elastic(item_id)
            if not item:
                return None
            await self._put_to_cache(item)
        return item

    async def _get_from_elastic(self, item_id: str) -> Optional[Union[Film, Person, Genre]]:
        """
        Get item from elasticsearch by item id.
        :param item_id: Item id.
        :return: Model.
        """
        try:
            doc = await self.elastic.get(self.name_model, item_id)
        except NotFoundError:
            return None
        return self.model(**doc['_source'])
