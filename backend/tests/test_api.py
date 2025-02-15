import json
import pytest
from fastapi import status
from unittest.mock import patch
from httpx import AsyncClient

from app.api.schemas.speech_to_text import TextRequest
from app.main import app


@pytest.mark.asyncio
async def test_process_speech_endpoint(redis_client, sample_audio_bytes, mock_speech_to_text):
    """Test the speech processing endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/speech",
            content=sample_audio_bytes,
            headers={"Content-Type": "application/octet-stream"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "request_id" in data
        assert "status" in data
        assert data["status"] == "Speech queued for processing"


@pytest.mark.asyncio
async def test_process_speech_empty_request(redis_client):
    """Test the speech processing endpoint with empty request body."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/speech",
            content=b"",
            headers={"Content-Type": "application/octet-stream"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "empty" in data["detail"].lower()


@pytest.mark.asyncio
async def test_process_text_endpoint(redis_client, sample_text):
    """Test the text processing endpoint."""
    request_data = TextRequest(text=sample_text)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/text",
            json=request_data.model_dump()
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "request_id" in data
        assert "status" in data
        assert data["status"] == "Text queued for processing"


@pytest.mark.asyncio
async def test_process_text_invalid_request(redis_client):
    """Test the text processing endpoint with invalid request."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/text",
            json={}  # Missing required 'text' field
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_speech_to_text_conversion(sample_audio_bytes):
    """Test the speech to text conversion function."""
    from app.api.routes.v1.ai import speech_to_text
    
    result = await speech_to_text(sample_audio_bytes)
    assert isinstance(result, str)
    assert len(result) > 0  # Should return non-empty string 