from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, schema_json_of
from pydantic.schema import Optional, List

from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    rating: float
    actors: Optional[List[Optional[dict]]]
    genres: Optional[List[Optional[dict]]]
    writers: Optional[List[Optional[dict]]]
    directors: Optional[List[Optional[dict]]]


@router.get('/')
async def get_all_movies(
    page_size: Optional[int] = Query(
        10,
        alias='page[size]',
        description='Items amount on page'),
    page_number: Optional[int] = Query(
        0,
        alias='page[number]',
        description='Page number for pagination',
    ),
    sort: str = '-imdb_rating',
    genre: Optional[str] = Query(
        '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff',
        alias='filter[genre]',
        description='genre uuid'
    ),

    film_service: FilmService = Depends(get_film_service),
) -> Film:

    sort_types = {'imdb_rating': 'acs', '-imdb_rating': 'desc'}
    order = sort_types[sort]

    films = await film_service.get_top_films(page_size=page_size, page_number=page_number, order=order, genre=genre)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')
    return films


@router.get('/search')
async def search_movie_by_word(search_word: str, page_size: int = 10,
                               page: int = 0,
                               film_service: FilmService = Depends(
                                   get_film_service),
                               ) -> Film:
    films = await film_service.get_by_search_word(search_word, page_size=page_size, page=page)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')
    return films


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
        # Которое отсутствует в модели ответа API.
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны
        # и, возможно, данные, которые опасно возвращать
    return Film(
        id=film.id,
        title=film.title,
        actors=film.actors,
        rating=film.rating,
        genres=film.genres,
        writers=film.writers,
        directors=film.directors,
    )
