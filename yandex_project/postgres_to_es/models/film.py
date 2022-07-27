from pydantic import Field, validator
from typing import Any

from .datetime import DateTimeMixin
from .person import Person
from .genre import Genre


class ElasticMovie(DateTimeMixin):
    id: str = None
    title: str = None
    description: str = None
    rating: float = None
    genres: list = list[Genre]
    actors_names: list = list()
    writers_names: list = list()
    director:  list = list()
    modified: Any = None
    actors: list[Person] = []
    writers: list[Person] = []

    @validator('modified', pre=True)
    def validate(cls, v, values, **kwargs):
        return f'{v}'
