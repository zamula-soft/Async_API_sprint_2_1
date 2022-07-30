from fastapi import APIRouter, Depends, Query

from services.person import PersonService, get_person_service
from api.v1.messges import message_not_found
from api.v1.models import Person, Films


router = APIRouter()


@router.get('/', response_model=Person)
async def get_all_persons(
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        service: PersonService = Depends(get_person_service),
        sort: str = Query(
            default='-full_name',
            regex='^-?full_name',
            description='You can use only: full_name, -full_name'),
) -> Person:
    """
    Get all persons (sorted by name by default).
    - **sort**: [-full_name, full_name]
    - **page_size**: page size
    - **page_number**: page number

    """

    persons = await service.get_persons(page_size=page_size, page_number=page_number, order_by=sort)
    return persons


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, service: PersonService = Depends(get_person_service)) -> Person:
    """
    Get person by id with all the information.
    - **person_id**: person uuid
    """

    person = await service.get_by_id(person_id)
    if not person:
        raise message_not_found(name_object='person', id_object=person_id)

    return Person(**person.dict())


@router.get('/{person_id}/films/', response_model=Films)
async def get_films_by_person(
        person_id: str,
        page_size: int = Query(ge=1, le=100, default=10),
        page_number: int = Query(default=0, ge=0),
        sort: str = Query(
            default='-rating',
            regex='^-?(rating|title)',
            description='You can use only: rating, -rating, title, -title'),
        role: str = Query(
            default='',
            regex='actor|writer|director',
            description='You can use only: actor, writer, director'),
        service: PersonService = Depends(get_person_service)):
    """
    Get all movies of a person (sorted by rating by default). 
    You can specify person's role to filter movies where person participated as an actor, writer or director.
    - **person_id**: person uuid
    - **role**: [actor, writer, director]
    - **sort**: [rating, -rating, title, -title]
    - **page_size**: page size
    - **page_number**: page number
    """

    if 'title' in sort:
        sort += '.keyword'

    films = await service.get_movies_by_person(
        person_id=person_id,
        page_size=page_size,
        page_number=page_number,
        order_by=sort,
        role=role,
    )

    return films
