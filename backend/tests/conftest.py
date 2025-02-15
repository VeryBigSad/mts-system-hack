import asyncio
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.core.redis import RedisClient, get_redis_client
from app.main import app  # You'll need to create this if it doesn't exist


# Set testing environment
os.environ["TESTING"] = "1"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def redis_client():
    """Create a mock Redis client for testing."""
    mock_redis = AsyncMock()
    
    # Configure the mock to return a success response for rpush
    async def mock_rpush(*args, **kwargs):
        return 1
    
    mock_redis.rpush = AsyncMock(side_effect=mock_rpush)
    
    # Mock the connection pool and client
    with patch('app.core.redis.aioredis.ConnectionPool'):
        with patch('app.core.redis.aioredis.Redis', return_value=mock_redis):
            with patch('app.core.redis.get_redis_client') as mock_get_redis:
                client = RedisClient()
                # Override the Redis client with our mock
                client._redis = mock_redis
                mock_get_redis.return_value = client
                yield client


@pytest.fixture
def test_client(redis_client):
    """Create a FastAPI TestClient instance."""
    with patch('app.core.redis.get_redis_client', return_value=redis_client):
        yield TestClient(app)


@pytest.fixture
def sample_audio_bytes():
    """Generate sample audio bytes for testing."""
    return b"fake audio data for testing"


@pytest.fixture
def sample_text():
    """Generate sample text for testing."""
    return "Sample text for processing"


@pytest.fixture
def mock_speech_to_text():
    """Mock the speech_to_text function."""
    async def mock_convert(*args, **kwargs):
        return "Mocked transcription result"
    
    with patch('app.api.routes.v1.ai.speech_to_text', new=mock_convert):
        yield mock_convert 