from functools import lru_cache

from pydantic import BaseSettings, Field


@lru_cache()
class TestSettings(BaseSettings):
    redis_host: str = Field('http://127.0.0.1', env='REDIS_HOST')
    redis_port: str = Field('6378', env='REDIS_PORT')

    project_name: str = "MOVIES"
    base_url: str = Field('http://localhost:8005/api/v1/', env='BASE_URL')

    elastic_host: str = Field('http://127.0.0.1', env='ES_HOST')
    elastic_port: str = Field('9201', env='ES_PORT')

    class Config:
        env_file = '.env_test'
