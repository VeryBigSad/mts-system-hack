"""
Redis client configuration and utility functions.
Provides methods for managing cache data, user settings, and temporary storage.
Implements connection pooling and transaction support.
"""

import logging
from functools import lru_cache

import redis.asyncio as aioredis

from app.core.configs.config import settings

logger = logging.getLogger(__name__)

SEVEN_DAYS_IN_SECONDS = 60 * 60 * 24 * 7


class RedisClient:
    def __init__(self):
        self._pool = aioredis.ConnectionPool.from_url(
            str(settings.REDIS_URL), max_connections=10, decode_responses=True
        )
        self._redis = aioredis.Redis(connection_pool=self._pool)

    async def get_user_language_by_id(self, id: int) -> str | None:
        """Get user language setting from cache"""
        return await self._redis.get(f"user:language:{id}")

    async def set_user_language_by_id(self, id: int, lang: str) -> None:
        """Set user language setting in cache"""
        await self._redis.set(f"user:language:{id}", lang, ex=SEVEN_DAYS_IN_SECONDS)

    async def is_user_blocked(self, user_id: int) -> bool:
        """Get user block status from cache using bitmap"""
        result = await self._redis.get(f"user:{user_id}:blocked")
        return result == "1"

    async def set_user_block_status(self, user_id: int, is_blocked: bool) -> None:
        """Set user block status in cache using bitmap"""
        await self._redis.set(f"user:{user_id}:blocked", int(is_blocked), ex=SEVEN_DAYS_IN_SECONDS)


@lru_cache()
def get_redis_client() -> RedisClient:
    """Get singleton instance of RedisClient"""
    return RedisClient()
