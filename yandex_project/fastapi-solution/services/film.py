from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import Film
from .result import get_result

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    """Service for get data from elasticsearch or redis"""

    def __init__(self, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param elastic: connect to Elasticsearch
        """

        self.elastic = elastic


class Cache:

    def __init__(self, redis: Redis):
        self.redis = redis

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        """
        Get film from Redis.
        :param film_id: Film id.
        :return: Model Film
        """
        film_id = f'api_cache::elastic::movies::{film_id}'
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film) -> None:
        """
        Save film to Redis. Create cache.
        :param film: Model Film
        :return:
        """
        film_id = f'api_cache::elastic::movies::{film.id}'
        await self.redis.set(film_id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


class FilmServiceGetByID(FilmService, Cache):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param redis: connect to Redis
        :param elastic: connect to Elasticsearch
        """
        super(FilmServiceGetByID, self).__init__(elastic=elastic)
        self.redis = redis

    async def get(self, film_id: str) -> Optional[Film]:
        """
        Get film by id.
        :param film_id: Film id.
        :return: Model Film
        """
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        """
        Get film from elasticsearch by film id.
        :param film_id: Film id.
        :return: Model Film.
        """
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])


class FilmServiceSearch(FilmService):

    async def get(self, search_word: str, page_size: int = 10, page_number: int = 0):

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


class FilmServiceGetFilms(FilmService):

    async def get(self, page_size: int = 10, page_number: int = 0, order_by: str = '-rating'):

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
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmServiceGetByID(elastic=elastic, redis=redis)


@lru_cache()
def get_film_service_get_films(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmServiceGetFilms(elastic)


@lru_cache()
def get_film_service_search_film(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmServiceSearch(elastic)

