from pydantic import BaseModel
from pydantic.schema import Dict, List, Optional

from .genres import Genre
from .persons import PersonForFilms
from .pagination import Pagination


class Film(BaseModel):
    id: str
    title: str
    rating: float
    genres: List[Optional[Genre]]
    actors: List[Optional[PersonForFilms]]
    writers: List[Optional[PersonForFilms]]
    directors: List[Optional[PersonForFilms]]


class Films(BaseModel):
    pagination: Pagination
    result: List[Film]
