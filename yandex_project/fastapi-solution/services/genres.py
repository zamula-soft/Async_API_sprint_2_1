from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from .result import get_result
from models.genre import Genre
from models.film import Film

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    """Service for get data from elasticsearch or redis"""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param redis: connect to Redis
        :param elastic: connect to Elasticsearch
        """
        self.redis = redis
        self.elastic = elastic

    async def get_genres(self, page_size: int = 10, page_number: int = 0, order_by: str = '-name'):

        order = 'asc'
        if order_by.startswith('-'):
            order = 'desc'

        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "sort": [
                {
                    "name.keyword": {
                        "order": order,
                    }
                }
            ]
        }

        resp = await self.elastic.search(index='genres', body=elastic_query)

        return get_result(resp=resp, page_size=page_size, page_number=page_number, model=Genre)

    async def get_movies_by_genre(
            self, genre_id: str = '', page_size: int = 10, page_number: int = 0, order_by: str = '-rating'):

        order = 'asc'
        if order_by.startswith('-'):
            order = 'desc'
            order_by = order_by[1:]

        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "query": {
                 "match": {
                   "genres.id.keyword": genre_id
                 }
               },
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

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        """
        Get genre by id.
        :param genre_id: genre.id.
        :return: Model Genre
        """
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        """
        Get genre from elasticsearch by genre id.
        :param genre_id: Genre id.
        :return: Model Genre.
        """
        genre_id = f'api_cache::elastic::genre::{genre_id}'
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        """
        Get genre from Redis.
        :param genre_id: genre.id.
        :return: Model Genre
        """
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre) -> None:
        """
        Save genre to Redis. Create cache.
        :param genre: genre.id
        :return:
        """
        genre_id = f'api_cache::elastic::genre::{genre.id}'
        await self.redis.set(genre_id, genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)