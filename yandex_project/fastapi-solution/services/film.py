from functools import lru_cache
from typing import Dict

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import Film
from .result import get_result
from .service import Service, ServiceGetByID, ABCStorage, get_elastic_storage_service
from .cache import RedisCache, AsyncCacheStorage, get_redis_storage_service_movies


class FilmServiceSearch:
    """Service for find film."""

    def __init__(self, storage: ABCStorage) -> None:
        """
        Init.
        :param storage: connect to Storage
        """
        self.storage = storage

    async def get(self, search_word: str, page_size: int = 10, page_number: int = 0) -> Dict:
        """
        Get film by keywords.
        :param search_word: keywords.
        :param page_size: count items on page.
        :param page_number: number of page.
        :return:
        """

        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "query": {
                "match": {
                    "title": {
                        "query": search_word
                    }
                }
            }
        }
        resp = await self.storage.search_from_storage(name_index='movies', query=elastic_query)

        return get_result(resp, page_size, page_number, Film)


class FilmServiceGetFilms:
    """Service for get all films."""

    def __init__(self, storage: ABCStorage) -> None:
        """
        Init.
        :param storage: connect to Storage
        """
        self.storage = storage

    async def get(self, page_size: int = 10, page_number: int = 0, order_by: str = '-rating'):
        """
        Get all films.
        :param page_size: count items on page.
        :param page_number: number of page.
        :param order_by: sorting by rating or title
        :return:
        """

        order = 'asc'
        if order_by.startswith('-'):
            order = 'desc'
            order_by = order_by[1:]

        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "sort": [
                {
                    order_by: {
                        "order": order,
                    }
                }
            ]
        }

        resp = await self.storage.search_from_storage(name_index='movies', query=elastic_query)

        return get_result(resp, page_size, page_number, Film)


@lru_cache()
def get_film_service_get_by_id(
        redis: AsyncCacheStorage = Depends(get_redis_storage_service_movies),
        storage: ABCStorage = Depends(get_elastic_storage_service),
) -> ServiceGetByID:
    return ServiceGetByID(storage=storage, cache_storage=redis)


@lru_cache()
def get_film_service_get_films(
        storage: ABCStorage = Depends(get_elastic_storage_service),
) -> FilmServiceGetFilms:
    return FilmServiceGetFilms(storage)


@lru_cache()
def get_film_service_search_film(
        storage: ABCStorage = Depends(get_elastic_storage_service),
) -> FilmServiceSearch:
    return FilmServiceSearch(storage)

