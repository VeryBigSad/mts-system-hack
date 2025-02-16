import asyncio
import uuid
from datetime import datetime, timedelta
import logging

from app.core.redis import get_redis_client
from app.api.schemas.ai import AIResponse

logger = logging.getLogger(__name__)
redis_client = get_redis_client()


async def wait_for_response(request_id: uuid.UUID, timeout: int = 30) -> AIResponse:
    """
    Wait for a response to be available in Redis for the given request ID.
    Polls Redis every 10ms for up to timeout seconds.
    Returns the response text or raises TimeoutError.
    """
    start_time = datetime.now()

    while (datetime.now() - start_time) < timedelta(seconds=timeout):
        # Check if response is available in Redis
        response = await redis_client.get_ai_response(str(request_id))
        if response is not None:
            return response

        # Wait before next check
        await asyncio.sleep(0.010)  # 10ms

    raise TimeoutError(f"No response received after {timeout} seconds")
