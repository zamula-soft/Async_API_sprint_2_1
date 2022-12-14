from functools import lru_cache

from fastapi import Depends

from .result import get_result
from .service import ServiceGetByID, ABCStorage, get_elastic_storage_service
from .cache import AsyncCacheStorage, get_redis_storage_service_genres
from models.genre import Genre
from models.film import Film


class GetAllGenres:

    def __init__(self, storage: ABCStorage) -> None:
        """
        Init.
        :param storage: connect to Storage
        """
        self.storage = storage

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

        resp = await self.storage.search_from_storage(name_index='genres', query=elastic_query)

        return get_result(resp=resp, page_size=page_size, page_number=page_number, model=Genre)


class GetMoviesByGenre:

    def __init__(self, storage: ABCStorage) -> None:
        """
        Init.
        :param storage: connect to Storage
        """
        self.storage = storage

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

        resp = await self.storage.search_from_storage(name_index='movies', query=elastic_query)

        return get_result(resp, page_size, page_number, Film)


@lru_cache()
def get_genres_service_get_by_id(
        redis: AsyncCacheStorage = Depends(get_redis_storage_service_genres),
        storage: ABCStorage = Depends(get_elastic_storage_service),
) -> ServiceGetByID:
    return ServiceGetByID(storage=storage, cache_storage=redis)


@lru_cache()
def get_genres_service_get_all(
        storage: ABCStorage = Depends(get_elastic_storage_service),
) -> GetAllGenres:
    return GetAllGenres(storage)


@lru_cache()
def get_films_service_get_by_genre(
        storage: ABCStorage = Depends(get_elastic_storage_service),
) -> GetMoviesByGenre:
    return GetMoviesByGenre(storage)
