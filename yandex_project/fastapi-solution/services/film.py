from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    """Service for get data from elasticsearch or redis"""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        """
        Init.
        :param redis: connect to Redis
        :param elastic: connect to Elasticsearch
        """
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """
        Get film by id.
        :param film_id: Film id.
        :return: Model Film
        """
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self._put_film_to_cache(film)
        return film

    async def get_by_search_word(self, search_word: str, page_size=10, page=1):
        elastic_query = {
            "size": page_size,
            "from": page*page_size,
            "query": {
                "match": {
                    "title": {
                        "query": search_word
                    }
                }
            }
        }
        resp = await self.elastic.search(index='movies', body=elastic_query)
        top_movies = resp['hits']['hits']
        res = []
        for m in top_movies:
            data = m['_source']
            res.append(
                {'id': data['id'],
                    'title': data['title'],
                    'rating': data['rating'],

                 })
        return res

    async def get_top_films(self, genre='', page_size: int = 10, page_number=0, order='asc'):
        # print('вошли в get_top_genre_top_movies ---', locals())

        elastic_query = {
            "size": page_size,
            "from": page_number*page_size,
            "_source": 'false',
            "fields": [
                {
                    "field": "genre"
                },

                {
                    "field": "id"
                },
                {
                    "field": "title"
                },

                {
                    "field": "rating"
                }
            ],
            "sort": [
                {
                    "rating": {
                        "order": order,
                        "missing": "_first",
                        "unmapped_type": "float"
                    }
                }
            ]
        }

        if genre:  # Если указан жанр, фильтруем по айди жанра
            elastic_query["query"] = {
                "term": {
                    "genres.id.keyword": {
                        "value": genre,
                        "boost": 1.0
                    }
                }
            }

        resp = await self.elastic.search(index='movies', body=elastic_query)
        total_entities_count = resp['hits']['total']['value']
        print('total_entities_count--', total_entities_count)

        # Считаем пагинацию, исходя из кол-ва результатов
        last_page = int(total_entities_count) // page_size - 1 if int(
            total_entities_count) % page_size == 0 else int(total_entities_count) // page_size
        next_page = page_number + 1 if page_number < last_page else None
        prev_page = page_number - 1 if (page_number-1) >= 0 else None

        # добавляем ее в начало каждого ответа (так вроде другие ребята делали)
        pagination_info = {'pagination': {
            'first': 0, 'last': last_page,
            'prev': prev_page, 'next': next_page}}

        res = [pagination_info]

        top_movies = resp['hits']['hits']
        for m in top_movies:
            print('movie ---', m)
            res.append(
                {
                    'id': m['fields']['id'][0],
                    'title': m['fields']['title'][0],
                    'rating': m['fields']['rating'][0],

                })

        return res

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

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        """
        Get film from Redis.
        :param film_id: Film id.
        :return: Model Film
        """
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film) -> None:
        """
        Save film to Redis. Create cache.
        :param film: Model Film
        :return:
        """
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)


