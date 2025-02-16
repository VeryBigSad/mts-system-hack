from fastapi import APIRouter

from app.api.routes.v1 import ai, ping_endpoint, text_to_speech, translator

router = APIRouter(prefix="/v1")

router.include_router(ping_endpoint.router, prefix="/ping")
router.include_router(ai.router, prefix="/ai")
router.include_router(translator.router, prefix="/translator")
router.include_router(text_to_speech.router, prefix="/tts")
