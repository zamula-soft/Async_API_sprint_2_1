from functools import lru_cache
from typing import Optional, Type

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models import Film
from .result import get_result
from .cache import Cache
from .service import Service


class FilmServiceGetByID(Service, Cache):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, name_model: str, model: Type[Film]) -> None:
        """
        Init.
        :param redis: connect to Redis
        :param elastic: connect to Elasticsearch
        :param name_model: name model for redis
        :param model: Model
        """
        super(FilmServiceGetByID, self).__init__(elastic=elastic)
        # Это место мне не очень нравится, но я не знаю, как сделать лучше.
        self.redis = redis
        self.name_model = name_model
        self.model = model

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


class FilmServiceSearch(Service):

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


class FilmServiceGetFilms(Service):

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
) -> FilmServiceGetByID:
    return FilmServiceGetByID(elastic=elastic, redis=redis, name_model='movies', model=Film)


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

