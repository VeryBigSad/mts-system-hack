import logging

from fastapi import APIRouter, status

from app.api.schemas.ping import PingResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ping"])


@router.get("", status_code=status.HTTP_200_OK)
async def ping() -> PingResponse:
    """Ping us!"""
    return {"ping": "pong!"}
