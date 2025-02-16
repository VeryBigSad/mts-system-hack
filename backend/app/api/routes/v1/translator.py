import logging
import uuid
import base64
import httpx

from gigachat import GigaChat
from app.api.schemas.ai import AIResponse, GigaChatResponse
from fastapi import APIRouter, HTTPException, status, Request

from app.core.redis import get_redis_client
from app.core.db.models import Request as RequestModel
from app.core.configs.config import settings

redis_client = get_redis_client()
logger = logging.getLogger(__name__)
router = APIRouter(tags=["processing"])

GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1"
gigachat_client = GigaChat(
    verify_ssl_certs=False,
    credentials=settings.GIGACHAT_TOKEN,
    scope='GIGACHAT_API_PERS',
    model='GigaChat-Max'
)
        

async def upload_image_to_gigachat(image_data: str) -> str:
    """Upload image to GigaChat and return file ID."""
    try:
        # Remove data:image/jpeg;base64, prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data)
        
        file_id = await gigachat_client.aupload_file(('image.jpg', image_bytes, 'image/jpeg'))
        return file_id.id_
    except Exception as e:
        logger.error(f"Error uploading image to GigaChat: {e}")
        raise


async def process_image_with_gigachat(file_id: str) -> dict:
    """Process image with GigaChat API."""
    try:

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Ты - система распознавания жестов русского жестового языка. Опиши, какой жест показан на изображении человеком, и определи его значение. В ответ дай одно слово или фразу, которую имеет ввиду человек, сделавший жест. Постарайся быть как можно точнее."
                },
                {
                    "role": "user",
                    "content": "Распознай жест на изображении",
                    "attachments": [file_id]
                }
            ],
        }
        result = await gigachat_client.achat(payload)

        return result.choices[0].message.content
                
    except Exception as e:
        logger.error(f"Error processing with GigaChat: {e}")
        raise


@router.post("/raspalcovka", status_code=status.HTTP_200_OK, response_model=GigaChatResponse)
async def process_gesture(request: Request) -> GigaChatResponse | None:
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
            
            return GigaChatResponse(text=response)
            
        except ValueError as e:
            raise ValueError(str(e))

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Error processing gesture: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing gesture")
