from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from services.genres import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str = None
    name: str = None


@router.get('/')
async def get_all_genres(
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        genre_service: GenreService = Depends(get_genre_service),
        sort: str = Query(
            default='-name',
            regex='^-?name',
            description='You can use only: name, -name'),
) -> Genre:

    genres = await genre_service.get_genres(page_size=page_size, page_number=page_number, order_by=sort)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genres


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