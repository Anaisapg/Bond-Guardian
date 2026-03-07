from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

# Check if we should use mock mode (for environments with network restrictions)
MOCK_MODE = os.environ.get("MOCK_DB", "false").lower() == "true"


class Database:
    """MongoDB database connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    is_mock: bool = False

    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        if MOCK_MODE:
            cls.is_mock = True
            logger.warning("Running in MOCK mode - no database connection")
            return

        try:
            # Add SSL options for better compatibility
            cls.client = AsyncIOMotorClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
            )

            # Test the connection
            await cls.client.admin.command('ping')

            # Get database name from URI or use default
            db_name = settings.mongodb_uri.split("/")[-1].split("?")[0]
            if not db_name or db_name == "":
                db_name = "bond_guardian"

            database = cls.client[db_name]

            # Import models here to avoid circular imports
            from app.models.user import User
            from app.models.contact import Contact
            from app.models.interaction import Interaction
            from app.models.reminder import Reminder
            from app.models.ritual_streak import RitualStreak
            from app.models.chat_message import ChatMessage

            # Initialize Beanie with all document models
            await init_beanie(
                database=database,
                document_models=[
                    User,
                    Contact,
                    Interaction,
                    Reminder,
                    RitualStreak,
                    ChatMessage,
                ]
            )

            logger.info(f"Connected to MongoDB: {db_name}")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.warning("Falling back to MOCK mode")
            cls.is_mock = True

    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")


async def get_database():
    """Dependency to get database client."""
    return Database.client
