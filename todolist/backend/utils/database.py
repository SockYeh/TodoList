from motor.motor_asyncio import AsyncIOMotorClient

from todolist.backend.utils.config import env

USER = env.MONGODB_USER
PASSWORD = env.MONGODB_PASSWORD
connection_str = env.MONGODB_URL.format(USER, PASSWORD)
client = None


async def open_db() -> None:
    """Open a connection to the MongoDB database."""
    global client  # noqa: PLW0603
    client = AsyncIOMotorClient(connection_str)


async def close_db() -> None:
    """Close the connection to the MongoDB database."""
    client.close()
