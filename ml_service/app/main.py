import asyncio
import logging
import orjson
import redis.asyncio as aioredis

from typing import Optional

from .agent import process_request
from .enums import InputType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = "redis://redis_db:6379"
PROCESSING_QUEUE_KEY = "ai:processing:queue"


class MLService:
    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        
    async def init_redis(self):
        """Initialize Redis connection"""
        if not self._redis:
            self._redis = aioredis.from_url(REDIS_URL, decode_responses=True)
            try:
                await self._redis.ping()
                logger.info("Successfully connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        
    async def process_queue(self) -> None:
        """Process requests from Redis queue"""
        await self.init_redis()
        
        while True:
            try:
                # Get the next request from the queue
                _, request_data = await self._redis.blpop(PROCESSING_QUEUE_KEY)
                request = orjson.loads(request_data)
                
                logger.info(f"Processing request: {request['request_uuid']}")
                
                # Process the request asynchronously
                result = await process_request(
                    input_data=request["text"],
                    input_type=InputType.TEXT
                )
                
                if result["status"] == "success":
                    # Store the result back in Redis
                    await self._redis.set(f"ai:complete:{str(request['request_uuid']).lower()}", orjson.dumps({
                        "response": result["text_response"]
                    }))
                    logger.info(f"Request {request['request_uuid']} processed successfully")
                else:
                    logger.error(f"Failed to process request {request['request_uuid']}: {result['message']}")
                    
            except asyncio.CancelledError:
                logger.info("Service shutdown initiated")
                break
            except Exception as e:
                logger.error(f"Error processing queue: {str(e)}", exc_info=True)
                await asyncio.sleep(0.001)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")


async def main():
    """Main entry point"""
    service = MLService()
    
    try:
        logger.info("ML Service starting...")
        await service.process_queue()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        await service.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
