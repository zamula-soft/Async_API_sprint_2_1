from functools import lru_cache

from pydantic import BaseSettings, Field


@lru_cache()
class RedisSettings(BaseSettings):
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: str = Field(..., env='REDIS_PORT')

    class Config:
        env_file = '.env'


@lru_cache()
class RedisConnection(BaseSettings):
    settings = RedisSettings()
    REDIS_URI: str = Field(f'redis://{settings.redis_host}:{settings.redis_port}')
