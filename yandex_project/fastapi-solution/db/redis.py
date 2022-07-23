from typing import Optional
from aioredis import Redis

redis: Optional[Redis] = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    """Connect for redis"""
    return redis
