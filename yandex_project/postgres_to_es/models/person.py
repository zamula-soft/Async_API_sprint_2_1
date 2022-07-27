from .datetime import DateTimeMixin


class Person(DateTimeMixin):
    id: str
    full_name: str

    class Config:
        allow_population_by_field_name = True
