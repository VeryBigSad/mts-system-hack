import logging

from fastapi import APIRouter, status
from redis import Redis
from tortoise import connections

from app.api.schemas.health import HealthResponse, HealthStatusModel
from app.core.configs.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


async def check_database_connection() -> bool:
    try:
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


async def check_redis_connection() -> bool:
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        return redis_client.ping()
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False


@router.get("/health", status_code=status.HTTP_200_OK, response_model=HealthResponse)
async def health_endpoint() -> HealthResponse:
    """Check the health status of all system components.

    This endpoint performs health checks on three critical system components:
    1. Database connection
    2. Redis connection

    Returns:
        dict: A dictionary containing:
            - health (str): Overall health status ('ok' if all checks pass, 'partial' otherwise)
            - status (dict): Individual status of each component:
                - database (bool): Database connection status
                - redis (bool): Redis connection status
    """
    database_connection: bool = await check_database_connection()
    redis_connection: bool = await check_redis_connection()
    health = database_connection and redis_connection

    return HealthResponse(
        health="ok" if health else "partial",
        status=HealthStatusModel(
            database=database_connection,
            redis=redis_connection,
        ),
    )
