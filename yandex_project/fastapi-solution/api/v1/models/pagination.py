from pydantic import BaseModel
from pydantic.schema import Optional


class Pagination(BaseModel):
    first: int
    last: int
    prev: Optional[int]
    next: Optional[int]
