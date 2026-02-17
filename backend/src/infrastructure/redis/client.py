from functools import lru_cache

from redis.asyncio import Redis

from src.config import get_redis_settings


@lru_cache
def get_redis() -> Redis:
    settings = get_redis_settings()
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
