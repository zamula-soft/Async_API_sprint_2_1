from .base_config import CustomBase
from pydantic.schema import Optional


class Film(CustomBase):
    """Film Model"""

    id: str
    title: str
    description: Optional[str]
    rating: Optional[float]
    actors: Optional[list]
    genres: Optional[list]
    directors: Optional[list]
    writers: Optional[list]