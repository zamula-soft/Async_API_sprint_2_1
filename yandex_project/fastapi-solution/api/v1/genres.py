from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic.schema import Optional, List, Dict

from services import GenreService, get_genre_service
from .custom_error import CustomNotFound

router = APIRouter()


class Genre(BaseModel):
    id: str = None
    name: str = None


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
    result: List[Film]


@router.get('/')
async def get_all_genres(
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        genre_service: GenreService = Depends(get_genre_service),
        sort: str = Query(
            default='name',
            regex='^-?name',
            description='You can use only: name, -name'),
) -> Genre:
    '''    Get all genres (sorted by name by default) 
        - **sort**: [name, -name]
        - **page_size**: page size
        - **page_number**: page number
    '''

    genres = await genre_service.get_genres(page_size=page_size, page_number=page_number, order_by=sort)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genres


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    ''' Get genre info (only genre name is available so far)
        - **genre_id**: genre uuid
    '''
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise CustomNotFound(name='genre', uid=genre_id)

    return Genre(
        **genre.dict())


@router.get('/{genre_id}/films/', response_model=Films)
async def get_films_by_genre(
        genre_id: str,
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        sort: str = Query(
            default='-rating',
            regex='^-?(rating|title)',
            description='You can use only: rating, -rating, title, -title'),
        genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    """
    Get all movies of a genre (sorted by ratings by default)
    - **genre_id**: genre uuid
    - **sort**: [rating, -rating, title, -title]
    - **page_size**: page size
    - **page_number**: page number

    """
    if 'title' in sort:
        sort += '.keyword'

    films = await genre_service.get_movies_by_genre(
        genre_id=genre_id,
        page_size=page_size,
        page_number=page_number,
        order_by=sort
    )

    return films
