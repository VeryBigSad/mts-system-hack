from fastapi import APIRouter

from app.api.routes.v1 import ping_endpoint, transcribe_speech

router = APIRouter(prefix="/v1")

router.include_router(ping_endpoint.router, prefix="/ping")
router.include_router(transcribe_speech.router, prefix="/speech_to_text")
