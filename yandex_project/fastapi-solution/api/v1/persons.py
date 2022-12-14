from fastapi import APIRouter, Depends, Query

from services import (
    ServiceGetByID,
    GetAllPersons,
    GetMoviesByPerson,
    get_persons_service_get_all,
    get_persons_service_get_by_id,
    get_films_service_get_by_person,
)
from api.v1.messges import message_not_found
from api.v1.models import Person, Films, Persons
from .paginator import Paginator


router = APIRouter()


@router.get('/', response_model=Persons)
async def get_all_persons(
        sort: str = Query(
            default='-full_name',
            regex='^-?full_name',
            description='You can use only: full_name, -full_name'),
        paginator: Paginator = Depends(),
        service: GetAllPersons = Depends(get_persons_service_get_all),
) -> Persons:
    """
    Get all persons (sorted by name by default).
    - **sort**: [-full_name, full_name]
    - **page_size**: page size
    - **page_number**: page number

    """

    persons = await service.get(page_size=paginator.page_size, page_number=paginator.page_number, order_by=sort)
    return Persons(pagination=persons['pagination'], result=persons['result'])


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, service: ServiceGetByID = Depends(get_persons_service_get_by_id)) -> Person:
    """
    Get person by id with all the information.
    - **person_id**: person uuid
    """

    person = await service.get(person_id)
    if not person:
        raise message_not_found(name_object='person', id_object=person_id)

    return Person(**person.dict())


@router.get('/{person_id}/films/', response_model=Films)
async def get_films_by_person(
        person_id: str,
        paginator: Paginator = Depends(),
        sort: str = Query(
            default='-rating',
            regex='^-?(rating|title)',
            description='You can use only: rating, -rating, title, -title'),
        role: str = Query(
            default='',
            regex='actor|writer|director',
            description='You can use only: actor, writer, director'),
        service: GetMoviesByPerson = Depends(get_films_service_get_by_person)) -> Films:
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

    films = await service.get(
        person_id=person_id,
        page_size=paginator.page_size,
        page_number=paginator.page_number,
        order_by=sort,
        role=role,
    )

    return Films(pagination=films['pagination'], result=films['result'])
