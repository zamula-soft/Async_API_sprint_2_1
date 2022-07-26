from functools import lru_cache
from typing import Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


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

    async def get_genres(self, count: int, order: str = 'desc'):

        elastic_query = {
            "size": count,
            "query": {
                "match_all": {}
            },
            "_source": 'false',
            "fields": [
                {
                    "field": "name"
                },
                {
                    "field": "id"
                },

            ],
            "sort": [
                {
                    "rating": {
                        "order": order,
                        "missing": "_last",
                        "unmapped_type": "float"
                    }
                }
            ]
        }
        resp = await self.elastic.search(index='genres', body=elastic_query)
        print('Get_top_genre_top_movies resp---', resp)

        top_movies = resp['hits']['hits']
        res = []
        for m in top_movies:
            res.append(
                {
                    'id': m['fields']['id'][0],
                    'name': m['fields']['name'][0],
                })

        return res

    async def get_movies_by_genre(self, genre_name: str = '', count: int = 10, order: str = 'desc'):
        print('вошли в get_top_genre_top_movies ---')
        print('genre_name ---- ', genre_name)

        query = {
            "match": {
                "genres": {
                    'id': genre_name,
                },
                }
            }

        if not genre_name:
            query = {
                    "match_all": {}
                }

        elastic_query = {
                "size" : count,
                "query" : query,
                "_source" : 'false',
                "fields" : [
                    {
                    "field" : "title"
                    },
                    {
                    "field" : "genre"
                    },
                    {
                    "field" : "rating"
                    },
                    {
                        "field": "id"
                    },
                    {
                        "field": ''
                    }

                ],
                "sort" : [
                    {
                    "rating" : {
                        "order" : order,
                        "missing" : "_last",
                        "unmapped_type" : "float"
                    }
                    }
                ]
                }
        resp = await self.elastic.search(index='movies',body=elastic_query)
        print('Get_top_genre_top_movies resp---', resp)
        # for e in resp:
        #     print('e---',e)
        top_movies = resp['hits']['hits']
        res = []
        for m in top_movies:
            # print('m---',m)
            res.append(
                {
                    'id': m['fields']['id'][0],
                    'title': m['fields']['title'][0],
                    'rating': m['fields']['rating'][0],

                })

        return res

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        """
        Get genre by id.
        :param genre_id: genre.id.
        :return: Model Genre
        """
        print('GenreService  get_by_id. genre_id =', genre_id)
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            print('genre from elastic --- ', genre)
            if not genre:
                print('NO GENRE!!')
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        """
        Get genre from elasticsearch by genre id.
        :param genre_id: Genre id.
        :return: Model Genre.
        """
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
        await self.redis.set(genre.id, genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)