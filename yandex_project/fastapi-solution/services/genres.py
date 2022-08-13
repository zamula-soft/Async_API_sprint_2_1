from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from .result import get_result
from .service import ServiceGetByID, Service
from models.genre import Genre
from models.film import Film


class GetAllGenres(Service):

    async def get(self, page_size: int = 10, page_number: int = 0, order_by: str = '-name'):

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


class GetMoviesByGenre(Service):

    async def get(
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


@lru_cache()
def get_genres_service_get_by_id(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> ServiceGetByID:
    return ServiceGetByID(elastic=elastic, redis=redis, name_model='genres', model=Genre)


@lru_cache()
def get_genres_service_get_all(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GetAllGenres:
    return GetAllGenres(elastic)


@lru_cache()
def get_films_service_get_by_genre(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GetMoviesByGenre:
    return GetMoviesByGenre(elastic)
