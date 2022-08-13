from functools import lru_cache
from typing import Dict

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import Film
from .result import get_result
from .service import Service, ServiceGetByID
from .cache import RedisCache, AsyncCacheStorage, get_redis_storage_service_movies


class FilmServiceSearch(Service):
    """Service for find film."""

    async def get(self, search_word: str, page_size: int = 10, page_number: int = 0) -> Dict:
        """
        Get film by keywords.
        :param search_word: keywords.
        :param page_size: count items on page.
        :param page_number: number of page.
        :return:
        """

        await self.check_elastic_connection()

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
        resp = await self.elastic.search(index='movies', body=elastic_query)

        return get_result(resp, page_size, page_number, Film)


class FilmServiceGetFilms(Service):
    """Service for get all films."""

    async def get(self, page_size: int = 10, page_number: int = 0, order_by: str = '-rating'):
        """
        Get all films.
        :param page_size: count items on page.
        :param page_number: number of page.
        :param order_by: sorting by rating or title
        :return:
        """

        await self.check_elastic_connection()

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

        resp = await self.elastic.search(index='movies', body=elastic_query)

        return get_result(resp, page_size, page_number, Film)


@lru_cache()
def get_film_service_get_by_id(
        redis: AsyncCacheStorage = Depends(get_redis_storage_service_movies),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> ServiceGetByID:
    return ServiceGetByID(elastic=elastic, cache_storage=redis)


@lru_cache()
def get_film_service_get_films(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmServiceGetFilms:
    return FilmServiceGetFilms(elastic)


@lru_cache()
def get_film_service_search_film(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmServiceSearch:
    return FilmServiceSearch(elastic)

