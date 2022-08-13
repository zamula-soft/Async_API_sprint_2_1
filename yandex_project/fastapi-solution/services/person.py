from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from models.film import Film
from .result import get_result
from .service import ServiceGetByID, Service
from .cache import AsyncCacheStorage, get_redis_storage_service_persons


class GetAllPersons(Service):

    async def get(self, page_size: int = 10, page_number: int = 0, order_by: str = '-full_name'):

        order = 'asc'
        if order_by.startswith('-'):
            order = 'desc'

        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "sort": [
                {
                    "full_name.keyword": {
                        "order": order,
                    }
                }
            ]
        }

        resp = await self.elastic.search(index='persons', body=elastic_query)

        return get_result(resp=resp, page_size=page_size, page_number=page_number, model=Person)


class GetMoviesByPerson(Service):

    async def get(
            self,
            person_id: str = '',
            page_size: int = 10,
            page_number: int = 0,
            order_by: str = '-rating',
            role: str = '',
    ):
        query = {
            "match": {
               f"{role}s.id.keyword": person_id
             }
           }

        if not role:
            query = {
                "bool": {
                    "should": [
                        {"match": {"writers.id.keyword": person_id}},
                        {"match": {"actors.id.keyword": person_id}},
                        {"match": {"directors.id.keyword": person_id}},
                    ],
                },
            }

        order = 'asc'
        if order_by.startswith('-'):
            order = 'desc'
            order_by = order_by[1:]

        elastic_query = {
            "size": page_size,
            "from": page_number * page_size,
            "query": query,
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
def get_persons_service_get_by_id(
        redis: AsyncCacheStorage = Depends(get_redis_storage_service_persons),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> ServiceGetByID:
    return ServiceGetByID(elastic=elastic, cache_storage=redis)


@lru_cache()
def get_persons_service_get_all(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GetAllPersons:
    return GetAllPersons(elastic)


@lru_cache()
def get_films_service_get_by_person(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GetMoviesByPerson:
    return GetMoviesByPerson(elastic)
