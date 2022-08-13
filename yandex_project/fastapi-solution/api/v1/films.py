from fastapi import APIRouter, Depends, Query

from services import (
    FilmServiceSearch,
    FilmServiceGetFilms,
    ServiceGetByID,
    get_film_service_search_film,
    get_film_service_get_films,
    get_film_service_get_by_id)
from api.v1.messges import message_not_found
from api.v1.models import Film, Films
from .paginator import Paginator

router = APIRouter()


@router.get('/', response_model=Films)
async def get_all_movies(
        sort: str = Query(
            default='-rating',
            regex='^-?(rating|title)',
            description='You can use only: rating, -rating, title, -title'),
        paginator: Paginator = Depends(),
        film_service: FilmServiceGetFilms = Depends(get_film_service_get_films),
) -> Films:
    """
    Get all movies (sorted by rating by default)
    - **sort**: [rating, -rating, title, -title]
    - **page_size**: page size
    - **page_number**: page number
    """
    if 'title' in sort:
        sort += '.keyword'

    films = await film_service.get(page_size=paginator.page_size, page_number=paginator.page_number, order_by=sort)

    return Films(pagination=films['pagination'], result=films['result'])


@router.get(
    '/search/',
    response_model=Films,
)
async def search_movie_by_word(
        search_word: str,
        paginator: Paginator = Depends(),
        film_service: FilmServiceSearch = Depends(get_film_service_search_film)
) -> Films:
    """
    Search film by word in title
    - **search_word**: search word
    - **page_size**: page size
    - **page_number**: page number

    """
    films = await film_service.get(search_word, page_size=paginator.page_size, page_number=paginator.page_number)

    return Films(pagination=films['pagination'], result=films['result'])


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}/', response_model=Film)
async def film_details(film_id: str, film_service: ServiceGetByID = Depends(get_film_service_get_by_id)) -> Film:
    """
    Get film by id with all the information.
    - **film_id**: film uuid
    """
    film = await film_service.get(film_id)
    if not film:
        raise message_not_found(name_object='film', id_object=film_id)
        
    return Film(**film.dict())
