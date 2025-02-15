import logging
import uuid

from app.api.schemas.ai import AIResponse
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.api.schemas.speech_to_text import TextRequest
from app.core.redis import get_redis_client
from app.core.db.models import Request as RequestModel
from app.core.connector import wait_for_response
from app.core.speech_to_text import speech_to_text, video_to_text

redis_client = get_redis_client()
logger = logging.getLogger(__name__)
router = APIRouter(tags=["processing"])


@router.post("/raspalcovka", status_code=status.HTTP_200_OK, response_model=AIResponse)
async def process_video(request: Request) -> AIResponse | None:
    """
    Process video from raw MP4 bytes.
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
            return None

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
            return None
            # return ProcessingResponse(request_id=str(request_uuid), status="Processing", response=None)

    except Exception as e:
        logger.exception(f"Error queueing text: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Error queueing text"})
