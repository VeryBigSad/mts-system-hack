import logging
import uuid
import base64
import httpx

from app.api.schemas.ai import AIResponse
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.api.schemas.speech_to_text import TextRequest
from app.core.redis import get_redis_client
from app.core.db.models import Request as RequestModel
from app.core.connector import wait_for_response
from app.core.speech_to_text import speech_to_text, video_to_text
from app.core.configs.config import settings

redis_client = get_redis_client()
logger = logging.getLogger(__name__)
router = APIRouter(tags=["processing"])

GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1"


@router.post("/video", status_code=status.HTTP_200_OK, response_model=AIResponse)
async def process_video(request: Request) -> AIResponse | None:
    """
    Process some photos.
    The request body should contain the raw bytes of an MP4 file.
    First converts video to text, then queues the text for processing.
    """
    try:
        # Read raw bytes from request body
        video_bytes = await request.body()
        logger.info("Received video data")

        if not video_bytes:
            raise ValueError("Request body is empty. Expected MP4 bytes.")

        # Generate unique ID for this request
        request_uuid = uuid.uuid4()

        # First convert speech to text
        try:
            text = await video_to_text(video_bytes)
        except ValueError as e:
            raise ValueError(str(e))

        # Queue the text processing request
        await redis_client.queue_text_request(str(request_uuid), text)

        # Save request to database for history
        await RequestModel.create(id=request_uuid, request_type="video", input_text=text, status="Processing")

        try:
            # Wait for response with timeout
            response = await wait_for_response(request_uuid)
            # Update database record with the response
            await RequestModel.filter(id=request_uuid).update(status="Completed", response=response)
            return response
        except TimeoutError:
            return None

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Error processing audio: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing audio")


@router.post("/speech", status_code=status.HTTP_200_OK, response_model=AIResponse)
async def process_speech(request: Request) -> AIResponse | None:
    """
    Process speech from raw MP3 bytes.
    The request body should contain the raw bytes of an MP3 file.
    First converts speech to text, then queues the text for processing.
    """
    try:
        # Read raw bytes from request body
        audio_bytes = await request.body()
        logger.info("Received audio data")

        if not audio_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body is empty. Expected MP3 bytes.")

        # Generate unique ID for this request
        request_uuid = uuid.uuid4()

        # First convert speech to text
        try:
            text = await speech_to_text(audio_bytes)
        except ValueError as e:
            raise ValueError(str(e))

        # Queue the text processing request
        await redis_client.queue_text_request(str(request_uuid), text)

        # Save request to database for history
        await RequestModel.create(id=request_uuid, request_type="speech", input_text=text, status="Processing")

        try:
            # Wait for response with timeout
            response = await wait_for_response(request_uuid)
            # Update database record with the response
            await RequestModel.filter(id=request_uuid).update(status="Completed", response=response)
            return response
        except TimeoutError:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Timeout waiting for response")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Error processing audio: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing audio")


@router.post("/text", status_code=status.HTTP_200_OK, response_model=AIResponse)
async def process_text(request: TextRequest) -> AIResponse:
    """
    Queue text for processing.
    """
    try:
        # Generate unique ID for this request
        request_uuid = uuid.uuid4()

        # Queue the text processing request
        await redis_client.queue_text_request(str(request_uuid), request.text)

        # Save request to database for history
        await RequestModel.create(id=request_uuid, request_type="text", input_text=request.text, status="Processing")

        try:
            # Wait for response with timeout
            response = await wait_for_response(request_uuid)
            # Update database record with the response
            await RequestModel.filter(id=request_uuid).update(status="Completed", response=response)
            return response
        except TimeoutError:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Timeout waiting for response")

    except Exception as e:
        logger.exception(f"Error queueing text: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error queueing text")


async def upload_image_to_gigachat(image_data: str) -> str:
    """Upload image to GigaChat and return file ID."""
    try:
        # Remove data:image/jpeg;base64, prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data)
        
        files = {
            'file': ('image.jpg', image_bytes, 'image/jpeg')
        }
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.GIGACHAT_TOKEN}'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GIGACHAT_API_URL}/files",
                headers=headers,
                files=files
            )
            
            if not response.is_success:
                raise ValueError(f"Failed to upload image: {response.text}")
            
            return response.json()['id']
    except Exception as e:
        logger.error(f"Error uploading image to GigaChat: {e}")
        raise


async def process_image_with_gigachat(file_id: str) -> dict:
    """Process image with GigaChat API."""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.GIGACHAT_TOKEN}'
        }
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты - система распознавания жестов. Опиши, какой жест показан на изображении, и определи его значение. Ответ дай в формате JSON с полями task (одно из значений: call_elevator, check_camera, check_snow, create_ticket, submit_readings, pay_utilities, check_obstacles) и parameters (необходимые параметры для задачи)."
                },
                {
                    "role": "user",
                    "content": "Распознай жест на изображении",
                    "attachments": [file_id]
                }
            ],
            "stream": False,
            "update_interval": 0
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GIGACHAT_API_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if not response.is_success:
                raise ValueError(f"Failed to process with GigaChat: {response.text}")
            
            result = response.json()
            # Parse the JSON response from the message content
            try:
                content = result['choices'][0]['message']['content']
                return {"status": "success", **eval(content)}
            except:
                return {
                    "status": "success",
                    "task": "create_ticket",
                    "parameters": {
                        "category": "other",
                        "description": content,
                        "priority": "normal",
                        "location": "не указано"
                    }
                }
                
    except Exception as e:
        logger.error(f"Error processing with GigaChat: {e}")
        raise


@router.post("/raspalcovka", status_code=status.HTTP_200_OK, response_model=AIResponse)
async def process_gesture(request: Request) -> AIResponse | None:
    """
    Process gesture image using GigaChat API.
    The request body should contain base64 encoded image.
    """
    try:
        # Read JSON from request body
        data = await request.json()
        image_data = data.get('image')
        
        if not image_data:
            raise ValueError("Request body must contain 'image' field with base64 encoded image")

        # Generate unique ID for this request
        request_uuid = uuid.uuid4()

        try:
            # Upload image to GigaChat
            file_id = await upload_image_to_gigachat(image_data)
            
            # Process with GigaChat
            response = await process_image_with_gigachat(file_id)
            
            # Save request to database
            await RequestModel.create(
                id=request_uuid,
                request_type="gesture",
                status="Completed",
                response=response
            )
            
            return response
            
        except ValueError as e:
            raise ValueError(str(e))

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Error processing gesture: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing gesture")
