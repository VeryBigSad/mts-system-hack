"""
Redis client configuration and utility functions.
Provides methods for managing cache data, user settings, and temporary storage.
Implements connection pooling and transaction support.
"""

import os
import logging

import orjson
import redis.asyncio as aioredis
from functools import lru_cache

from app.core.configs.config import settings
from app.api.schemas.ai import AIResponse

logger = logging.getLogger(__name__)

SEVEN_DAYS_IN_SECONDS = 60 * 60 * 24 * 7
PROCESSING_QUEUE_KEY = "ai:processing:queue"


class RedisClient:
    def __init__(self):
        # Use test URL in test environment
        redis_url = "redis://localhost:6379" if os.getenv("TESTING") else str(settings.REDIS_URL)
        self._pool = aioredis.ConnectionPool.from_url(redis_url, max_connections=10, decode_responses=True)
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

    async def queue_text_request(self, request_uuid: str, text: str) -> None:
        """
        Add a text processing request to the queue.

        Args:
            request_uuid: Unique identifier for the request
            text: Text to be processed
        """
        try:
            request_data = {
                "request_uuid": request_uuid,
                "text": text,
            }

            # Add to the processing queue
            await self._redis.rpush(PROCESSING_QUEUE_KEY, orjson.dumps(request_data))
            logger.info(f"Queued text request {request_uuid}")

        except Exception as e:
            logger.error(f"Error queueing text request: {e}")
            raise

    async def get_ai_response(self, request_uuid: str) -> str | None:
        """
        Get AI response for a specific request ID.

        Args:
            request_uuid: Unique identifier for the request

        Returns:
            The response text if available, None otherwise
        """
        try:
            response_data = await self._redis.get(f"ai:complete:{request_uuid}")
            if response_data:
                # Parse and validate the response
                try:
                    response_json = orjson.loads(response_data)
                    response = AIResponse.model_validate(response_json)
                    # Clean up the key after retrieving
                    await self._redis.delete(f"ai:complete:{request_uuid}")
                    return response.ai_response
                except Exception as e:
                    logger.error(f"Invalid AI response format: {e}")
                    return None
            return None
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return None

    async def set_ai_response(self, request_uuid: str, response: str) -> None:
        """
        Set AI response for a specific request ID.

        Args:
            request_uuid: Unique identifier for the request
            response: The AI's response text
        """
        try:
            # Create and validate the response object
            response_obj = AIResponse(ai_response=response)
            # Store the validated response
            await self._redis.set(f"ai:complete:{request_uuid}", orjson.dumps(response_obj.model_dump()))
            logger.info(f"Set AI response for request {request_uuid}")
        except Exception as e:
            logger.error(f"Error setting AI response: {e}")
            raise


@lru_cache()
def get_redis_client() -> RedisClient:
    """Get singleton instance of RedisClient"""
    return RedisClient()
