from pydantic import BaseModel
from pydantic.schema import Dict, List, Optional

from .genres import Genre
from .persons import Person


class Film(BaseModel):
    id: str
    title: str
    rating: float
    genres: Optional[List[Optional[Genre]]]
    actors: Optional[List[Optional[Person]]]
    writers: Optional[List[Optional[Person]]]
    directors: Optional[List[Optional[Person]]]


class Films(BaseModel):
    pagination: Dict
    result: List[Film]
