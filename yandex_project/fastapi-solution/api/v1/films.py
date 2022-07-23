from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    actors: list


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    print('film get api', film)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
                # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
        # Которое отсутствует в модели ответа API.
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны
        # и, возможно, данные, которые опасно возвращать
    return Film(id=film.id, title=film.title, actors=film.actors)


# {
#     'id': 'e859508c-3e82-4e8c-93f8-32d1b4aba330',
#     'rating': 5.0,
#     'genre': ['test_genre'],
#     'title': 'test',
#     'description': 'destt',
#     'directors_names': ['Director'],
#     'actors_names': ['Actor'],
#     'writers_names': ['Writer'],
#     'writers': [{'id': '5408ceb8-2ee4-443d-9712-c559bbda36a6', 'name': 'Writer'}],
#     'actors': [{'id': '1add561e-26f4-4284-9da1-d396e4a16b93', 'name': 'Actor'}],
#     'directors': [{'id': '1e69e33d-ba8b-47b7-91d9-023a1fb296d0', 'name': 'Director'}],
#     'genres': [{'id': 'f8a1d633-15ac-4be6-b801-3d3c21e5e702', 'name': 'test_genre'}]
# }