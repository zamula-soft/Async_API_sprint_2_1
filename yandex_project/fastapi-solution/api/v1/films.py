from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from pydantic.schema import Dict, List, Optional
from services.film import FilmService, get_film_service

from .custom_error import CustomNotFound

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
    '''    Get all movies (sorted by rating by default) 
        - **sort**: [rating, -rating, title, -title]
        - **page_size**: page size
        - **page_number**: page number
    '''
    if 'title' in sort:
        sort += '.keyword'

    films = await film_service.get_films(page_size=page_size, page_number=page_number, order_by=sort)

    return Films(pagination=films['pagination'], result=films['result'])


@router.get('/search/')
async def search_movie_by_word(
        search_word: str,
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        film_service: FilmService = Depends(get_film_service)
) -> Films:
    """
    Search film by word in title 
    - **search_word**: search word
    - **page_size**: page size
    - **page_number**: page number

    """
    films = await film_service.get_by_search_word(search_word, page_size=page_size, page_number=page_number)

    return Films(pagination=films['pagination'], result=films['result'])


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}/', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    """
    Get film by id with all the information.
    - **film_id**: film uuid
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise CustomNotFound(name='film', uid=film_id )
    return Film(
        id=film.id,
        title=film.title,
        actors=film.actors,
        rating=film.rating,
        genres=film.genres,
        writers=film.writers,
        directors=film.directors,
    )
