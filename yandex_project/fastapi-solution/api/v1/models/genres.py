from pydantic import BaseModel
from pydantic.schema import List, Optional

from .pagination import Pagination


class Genre(BaseModel):
    id: str = None
    name: str = None


class Genres(BaseModel):
    pagination: Pagination
    result: List[Optional[Genre]]
