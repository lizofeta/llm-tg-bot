from redis.asyncio import Redis as AsyncRedis
import redis
from functools import lru_cache

from app.core.config import settings

@lru_cache
def get_redis():
    return AsyncRedis.from_url(
        str(settings.redis_url),
        decode_responses=True
    )


@lru_cache
def get_sync_redis():
    return redis.Redis.from_url(
        str(settings.redis_url),
        decode_responses=True
    )

redis_client = get_redis()
sync_redis_client = get_sync_redis()
