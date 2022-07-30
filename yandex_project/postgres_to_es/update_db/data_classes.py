import uuid
from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class UUID:
    id: uuid.UUID


@dataclass(frozen=True)
class TimeStamped:
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class FilmWork(UUID, TimeStamped):
    __slots__ = (
        'id', 'title', 'description', 'creation_date', 'rating', 'type', 'created_at', 'updated_at', 'file_path')
    type: str
    title: str
    rating: float
    description: str
    creation_date: datetime
    file_path: str


@dataclass(frozen=True)
class Genre(UUID, TimeStamped):
    __slots__ = ('id', 'name', 'description', 'created_at', 'updated_at')
    name: str
    description: str


@dataclass(frozen=True)
class Person(UUID, TimeStamped):
    __slots__ = ('id', 'full_name', 'created_at', 'updated_at')
    full_name: str


@dataclass(frozen=True)
class GenreFilmWork(UUID):
    __slots__ = ('id', 'genre_id', 'film_work_id', 'created_at')
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    created_at: datetime


@dataclass(frozen=True)
class PersonFilmWork(UUID):
    __slots__ = ('id', 'person_id', 'film_work_id', 'role', 'created_at')
    role: str
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    created_at: datetime
