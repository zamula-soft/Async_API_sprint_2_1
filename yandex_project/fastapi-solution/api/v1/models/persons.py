from pydantic import BaseModel
from pydantic.schema import List

from .pagination import Pagination


class Person(BaseModel):
    id: str
    full_name: str


class PersonForFilms(BaseModel):
    id: str
    name: str


class Persons(BaseModel):
    pagination: Pagination
    result: List[Person]
