from .datetime import DateTimeMixin


class Genre(DateTimeMixin):
    id: str
    name: str
    description: str = None

    class Config:
        allow_population_by_field_name = True
