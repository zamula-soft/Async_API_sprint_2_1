from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from models.film import Film
from .result import get_result

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    """Service for get data from elasticsearch or redis"""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param redis: connect to Redis
        :param elastic: connect to Elasticsearch
        """
        self.redis = redis
        self.elastic = elastic

    async def get_persons(self, page_size: int = 10, page_number: int = 0, order_by: str = '-full_name'):

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

    async def get_movies_by_person(
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

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Get person by id.
        :param person_id: person id.
        :return: Model Person
        """
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        """
        Get person from elasticsearch by + id.
        :param person_id: Person.id.
        :return: Model Person.
        """
        try:
            doc = await self.elastic.get('persons', person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        """
        Get person from Redis.
        :param person_id: person id.
        :return: Model Person
        """
        person_id = f'api_cache::elastic::persons::{person_id}'
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person) -> None:
        """
        Save person to Redis. Create cache.
        :param person: person.id
        :return:
        """
        person_id = f'api_cache::elastic::persons::{person.id}'
        await self.redis.set(person_id, person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
