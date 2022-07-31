from fastapi import APIRouter, Depends, Query

from services import GenreService, get_genre_service
from api.v1.messges import message_not_found
from api.v1.models import Genre, Films, Genres


router = APIRouter()


@router.get('/', response_model=Genres)
async def get_all_genres(
        page_size: int = Query(
            ge=1,
            le=100,
            default=10,
            alias='page[size]',
            description='Items amount on page',
        ),
        page_number: int = Query(
            default=0,
            alias='page[number]',
            description='Page number for pagination',
            ge=0),
        sort: str = Query(
            default='name',
            regex='^-?name',
            description='You can use only: name, -name'),
        genre_service: GenreService = Depends(get_genre_service),
) -> Genres:
    """
    Get all genres (sorted by name by default)
    - **sort**: [name, -name]
    - **page_size**: page size
    - **page_number**: page number
    """

    genres = await genre_service.get_genres(page_size=page_size, page_number=page_number, order_by=sort)
    return genres


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    """
    Get genre info (only genre name is available so far)
    - **genre_id**: genre uuid
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise message_not_found(name_object='genre', id_object=genre_id)

    return Genre(**genre.dict())


@router.get('/{genre_id}/films/', response_model=Films)
async def get_films_by_genre(
        genre_id: str,
        page_size: int = Query(
            ge=1,
            le=100,
            default=10,
            alias='page[size]',
            description='Items amount on page',
        ),
        page_number: int = Query(
            default=0,
            alias='page[number]',
            description='Page number for pagination',
            ge=0),
        sort: str = Query(
            default='-rating',
            regex='^-?(rating|title)',
            description='You can use only: rating, -rating, title, -title'),
        genre_service: GenreService = Depends(get_genre_service)) -> Films:
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

    return Films(pagination=films['pagination'], result=films['result'])
