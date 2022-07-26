from flask import g
from pydantic import Field, validator
from typing import Any

from .Datetime import DateTimeMixin
from .Person import Person
from .Genre import Genre


class ElasticMovie(DateTimeMixin):
    id: str = None
    title: str = None
    description: str = None
    imdb_rating: float = Field(None, alias='rating')
    genre: list = list[Genre]
    actors_names: list = list()
    writers_names: list = list()
    director:  list = list()
    modified: Any = None
    actors: list[Person] = []
    writers: list[Person] = []

    @validator('modified', pre=True)
    def validate(cls, v, values, **kwargs):
        return f'{v}'
