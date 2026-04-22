from redis.asyncio import Redis
from functools import lru_cache

from app.core.config import settings

@lru_cache
def get_redis():
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True
    )

redis_client = get_redis()
