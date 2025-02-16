import logging
import uuid
import base64
import httpx

from app.api.schemas.ai import AIResponse
from fastapi import APIRouter, HTTPException, status, Request

from app.core.redis import get_redis_client
from app.core.db.models import Request as RequestModel
from app.core.configs.config import settings

redis_client = get_redis_client()
logger = logging.getLogger(__name__)
router = APIRouter(tags=["processing"])

GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1"


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
