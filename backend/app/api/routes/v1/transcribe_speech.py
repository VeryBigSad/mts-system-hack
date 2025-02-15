import logging

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse

from app.api.schemas.speech_to_text import SpeechToTextResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["speech_to_text"])


@router.post("", status_code=status.HTTP_200_OK)
async def transcribe_speech(request: Request) -> SpeechToTextResponse:
    """
    Transcribe speech from raw MP3 bytes.
    The request body should contain the raw bytes of an MP3 file.
    """
    try:
        # Read raw bytes from request body
        audio_bytes = await request.body()
        logger.info(f"Received audio bytes: {audio_bytes}")
        if not audio_bytes:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Request body is empty. Expected MP3 bytes."}
            )
            
        # TODO: Add your MP3 processing logic here
        # For now, returning dummy response
        return SpeechToTextResponse(text="Hello, world! got audio bytes")
        
    except Exception as e:
        logger.exception(f"Error processing audio {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Error processing audio"}
        )
