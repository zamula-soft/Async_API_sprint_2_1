from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic.schema import Optional, List, Dict

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


class Films(BaseModel):
    pagination: Dict
    result: List


@router.get('/')
async def get_all_movies(
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        sort: str = Query(
            default='-rating',
            regex='^-?(rating|title)',
            description='You can use only: rating, -rating, title, -title'),
        film_service: FilmService = Depends(get_film_service),
) -> Films:

    if 'title' in sort:
        sort += '.keyword'

    films = await film_service.get_films(page_size=page_size, page_number=page_number, order_by=sort)

    return Films(pagination=films['pagination'], result=films['result'])


@router.get('/search/')
async def search_movie_by_word(
        search_word: str,
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        film_service: FilmService = Depends(get_film_service),
) -> Films:
    films = await film_service.get_by_search_word(search_word, page_size=page_size, page_number=page_number)

    return Films(pagination=films['pagination'], result=films['result'])


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}/', response_model=Film)
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
    return Film(**film.dict())
