import logging

from tortoise import Tortoise

from app.core.configs.config import settings

db_url = "postgres://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
logger = logging.getLogger(__name__)


async def init_db():
    logger.info("Initializing database")
    await Tortoise.init(
        db_url=db_url.format(
            DB_USERNAME=settings.DB_USERNAME,
            DB_PASSWORD=settings.DB_PASSWORD,
            DB_HOST=settings.DB_HOST,
            DB_PORT=settings.DB_PORT,
            DB_NAME=settings.DB_NAME,
        ),
        modules={"models": ["app.core.db.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db():
    logger.info("Closing database connection")
    await Tortoise.close_connections()
