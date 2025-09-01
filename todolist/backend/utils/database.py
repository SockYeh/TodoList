from motor.motor_asyncio import AsyncIOMotorClient

from todolist.backend.utils.config import env

USER = env.MONGODB_USER
PASSWORD = env.MONGODB_PASSWORD
connection_str = env.MONGODB_URL.format(USER, PASSWORD)
client = None


async def open_db() -> None:
    """Open a connection to the MongoDB database."""
    global client, users_db  # noqa: PLW0603
    client = AsyncIOMotorClient(connection_str)
    users_db = client["users"]


async def close_db() -> None:
    """Close the connection to the MongoDB database."""
    client.close()


async def create_user_db() -> None:
    """Create the user database."""
    await client.drop_database("users")

    auth_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["username", "email", "password"],
            "properties": {
                "username": {
                    "bsonType": "string",
                    "description": "must be a string. Spotify username of the user",
                },
                "email": {
                    "bsonType": "string",
                    "description": "must be a string. Email of the user",
                },
                "password": {
                    "bsonType": "string",
                    "description": "must be a string. Password of the user",
                },
            },
        },
    }

    await users_db.create_collection("auth_details")

    await users_db.command("collMod", "auth_details", validator=auth_validator)

    await users_db.auth_details.create_index("username", unique=True)
    await users_db.auth_details.create_index("email", unique=True)
