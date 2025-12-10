from typing import Sequence

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import Settings
from app.models.todo import Todo


async def init_db(settings: Settings) -> None:
    """
    Initialize Mongo connection and Beanie ODM.
    This is similar to connecting Mongoose with schemas.
    """
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db]

    # register document models here
    await init_beanie(database=db, document_models=[Todo])


def get_database_client(settings: Settings) -> AsyncIOMotorClient:
    """
    Expose the raw Motor client if you ever need it.
    Not strictly needed for Beanie usage.
    """
    return AsyncIOMotorClient(settings.mongo_uri)
