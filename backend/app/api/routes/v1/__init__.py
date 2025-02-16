from fastapi import APIRouter

from app.api.routes.v1 import ai, ping_endpoint, translator

router = APIRouter(prefix="/v1")

router.include_router(ping_endpoint.router, prefix="/ping")
router.include_router(ai.router, prefix="/ai")
router.include_router(translator.router, prefix="/translator")
