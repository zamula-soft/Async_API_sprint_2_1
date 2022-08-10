from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import Film
from .result import get_result
from .service import Service, ServiceGetByID


class FilmServiceSearch(Service):

    async def get(self, search_word: str, page_size: int = 10, page_number: int = 0):

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

    async def get(self, page_size: int = 10, page_number: int = 0, order_by: str = '-rating'):

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
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> ServiceGetByID:
    return ServiceGetByID(elastic=elastic, redis=redis, name_model='movies', model=Film)


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

