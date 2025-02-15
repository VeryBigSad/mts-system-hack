import logging
import uuid

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse

from app.api.schemas.speech_to_text import TextRequest, ProcessingResponse
from app.core.redis import get_redis_client
from app.core.db.models import Request as RequestModel
from app.core.connector import wait_for_response
from app.core.speech_to_text import speech_to_text

redis_client = get_redis_client()
logger = logging.getLogger(__name__)
router = APIRouter(tags=["processing"])


@router.post("/speech", status_code=status.HTTP_200_OK, response_model=ProcessingResponse)
async def process_speech(request: Request) -> ProcessingResponse:
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
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Request body is empty. Expected MP3 bytes."},
            )

        # Generate unique ID for this request
        request_uuid = uuid.uuid4()

        # First convert speech to text
        try:
            text = await speech_to_text(audio_bytes)
        except ValueError as e:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)})

        # Queue the text processing request
        await redis_client.queue_text_request(str(request_uuid), text)

        # Save request to database for history
        await RequestModel.create(id=request_uuid, request_type="speech", input_text=text, status="Processing")

        try:
            # Wait for response with timeout
            response = await wait_for_response(request_uuid)
            # Update database record with the response
            await RequestModel.filter(id=request_uuid).update(status="Completed", response=response)
            return ProcessingResponse(request_id=str(request_uuid), status="Completed", response=response)
        except TimeoutError:
            return ProcessingResponse(request_id=str(request_uuid), status="Processing", response=None)

    except Exception as e:
        logger.exception(f"Error processing audio: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Error processing audio"})


@router.post("/text", status_code=status.HTTP_200_OK, response_model=ProcessingResponse)
async def process_text(request: TextRequest) -> ProcessingResponse:
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
            return ProcessingResponse(request_id=str(request_uuid), status="Completed", response=response)
        except TimeoutError:
            return ProcessingResponse(request_id=str(request_uuid), status="Processing", response=None)

    except Exception as e:
        logger.exception(f"Error queueing text: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Error queueing text"})
