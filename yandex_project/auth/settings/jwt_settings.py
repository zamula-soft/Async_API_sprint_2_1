from functools import lru_cache
from datetime import timedelta

from pydantic import BaseSettings, Field


@lru_cache()
class JWTSettings(BaseSettings):
    jwt_secret_key: str = Field(..., env='JWT_SECRET_KEY')
    jwt_access_token_expires: timedelta = Field(..., env='JWT_ACCESS_TOKEN_EXPIRES')
    jwt_refresh_token_expires: str = Field(..., env='JWT_REFRESH_TOKEN_EXPIRES')
    jwt_error_message_key: str = Field(..., env='JWT_ERROR_MESSAGE_KEY')

    class Config:
        env_file = '.env'
