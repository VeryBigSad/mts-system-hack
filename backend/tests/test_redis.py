import json
import pytest

from app.core.redis import PROCESSING_QUEUE_KEY


@pytest.mark.asyncio
async def test_queue_text_request(redis_client, sample_text):
    """Test queueing a text processing request."""
    # Generate a test UUID
    test_uuid = "123e4567-e89b-12d3-a456-426614174000"
    
    # Call the method
    await redis_client.queue_text_request(test_uuid, sample_text)
    
    # Verify the call to rpush was made correctly
    redis_client._redis.rpush.assert_called_once()
    call_args = redis_client._redis.rpush.call_args[0]
    
    # Check the queue key
    assert call_args[0] == PROCESSING_QUEUE_KEY
    
    # Parse the JSON data that was queued
    queued_data = json.loads(call_args[1])
    assert queued_data["request_uuid"] == test_uuid
    assert queued_data["type"] == "text"
    assert queued_data["text"] == sample_text


@pytest.mark.asyncio
async def test_queue_text_request_error_handling(redis_client, sample_text):
    """Test error handling when queueing a text request fails."""
    redis_client._redis.rpush.side_effect = Exception("Redis connection error")
    
    with pytest.raises(Exception):
        await redis_client.queue_text_request("test-uuid", sample_text) 