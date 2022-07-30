from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings, Field

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: str = Field(..., env='REDIS_PORT')

    project_name: str = "MOVIES"

    elastic_host: str = Field(..., env='ES_HOST')
    elastic_port: str = Field(..., env='ES_PORT')

    class Config:
        env_file = '.env'


settings = Settings()
