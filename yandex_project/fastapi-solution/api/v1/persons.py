from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str = None
    full_name: str = None


@router.get('/')
async def get_all_persons(
        count: int = 10,
        order: str = 'desc',
        genre_service: PersonService = Depends(get_person_service),
) -> Person:

    if count > 100:
        count = 100

    films = await genre_service.get_persons(count=count, order=order)
    if not films:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return films


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    return Person(
        **person.dict())