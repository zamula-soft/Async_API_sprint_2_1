from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.genres import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str = None
    name: str = None


@router.get('/')
async def get_all_genres(
        count: int = 10,
        order: str = 'desc',
        genre_service: GenreService = Depends(get_genre_service),
) -> Genre:

    if count > 100:
        count = 100

    films = await genre_service.get_genres(count=count, order=order)
    if not films:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return films


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')
    return Genre(
        **genre.dict())


@router.get('/{genre_id}/films/', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    films = await genre_service.get_movies_by_genre(genre_id)
    if not films:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return films