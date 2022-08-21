from functools import lru_cache

from pydantic import BaseSettings, Field


@lru_cache()
class FlaskSettings(BaseSettings):
    flask_hos: str = Field(..., env='FLASK_HOST')
    flask_port: str = Field(..., env='FLASK_PORT')

    class Config:
        env_file = '.env'
