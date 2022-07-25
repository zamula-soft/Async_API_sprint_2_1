from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person

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

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Get person by id.
        :param person_id: person id.
        :return: Model Person
        """
        print('PersonService  get_by_id. person_id =', person_id)
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            print('person from elastic --- ', person)
            if not person:
                print('NO person!!')
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
        await self.redis.set(person.id, person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
