from functools import lru_cache

from pydantic import BaseSettings, Field


@lru_cache()
class PostgresSettings(BaseSettings):
    postgres_user: str = Field(..., env='DB_AUTH_USER')
    postgres_password: str = Field(..., env='DB_AUTH_PASSWORD')
    postgres_host: str = Field(..., env='DB_AUTH_HOST')
    postgres_port: str = Field(..., env='DB_AUTH_PORT')
    postgres_name: str = Field(..., env='DB_AUTH_NAME')

    class Config:
        env_file = '.env'


@lru_cache()
class PostgresConnection(BaseSettings):

    settings = PostgresSettings()

    SQLALCHEMY_DATABASE_URI: str = Field(
        f'postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}'
        f'@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_name}', description='for auth service'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = True
