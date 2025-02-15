"""
Core service layer for user-related operations.

Provides functions for managing user data and preferences:
- Language preferences caching and retrieval
- User data validation and processing
- Integration with Redis cache and database
"""

import logging

from tortoise.exceptions import DoesNotExist

from app.core.db.models import User
from app.core.redis import RedisClient, get_redis_client

logger = logging.getLogger(__name__)


async def get_user_language(user_id: int) -> str | None:
    """Get cached user language or re-cache new one from database"""
    redis_client: RedisClient = get_redis_client()
    result = await redis_client.get_user_language_by_id(user_id)
    if result is None:
        logger.debug(f"Re-caching user language, id={user_id}")
        try:
            result = (await User.get(id=user_id).only("language_code")).language_code
        except DoesNotExist:
            logger.warning(f"User with id={user_id} not found when caching language_code")
            return None
        logger.debug(f"Caching user_id={user_id} language={result}")
        await redis_client.set_user_language_by_id(user_id, result)
    return result


async def await_something(something):
    return await something
