from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pydantic import BaseModel
from pymongo import errors

from todolist.backend.schemas.tasks import TaskCreate, TaskUpdate
from todolist.backend.utils.config import env

USER = env.MONGODB_USER
PASSWORD = env.MONGODB_PASSWORD
connection_str = env.MONGODB_URL.format(USER, PASSWORD)
client = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DBErrors:
    """Database errors."""

    class UserExists(Exception):  # noqa: N818
        """User already exists error."""

    class UserNotFound(Exception):  # noqa: N818
        """User not found error."""

    class PasswordMismatch(Exception):  # noqa: N818
        """Password mismatch error."""

    class TaskNotFound(Exception):  # noqa: N818
        """Task not found error."""

    class TaskExists(Exception):  # noqa: N818
        """Task already exists error."""


def switch_id_to_pydantic(data: dict) -> dict:
    """Switches the id key to _id for pydantic models."""
    data["id"] = data["_id"]
    del data["_id"]
    return data


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(plain_password)


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


class UserModel(BaseModel):
    """User model for Pydantic validation."""

    id: ObjectId
    email: str
    username: str
    model_config = {"arbitrary_types_allowed": True}


async def create_user(email: str, username: str, password: str) -> bool:
    """Create a new user in the database."""
    user = {
        "email": email,
        "username": username,
        "password": hash_password(password),
    }
    try:
        await users_db.auth_details.insert_one(user)
    except errors.DuplicateKeyError as e:
        raise DBErrors.UserExists from e
    return True


async def authenticate_user(email: str, password: str) -> UserModel:
    """Authenticate a user."""
    user = await users_db.auth_details.find_one({"email": email})
    if not user:
        raise DBErrors.UserNotFound
    if not verify_password(password, user["password"]):
        raise DBErrors.PasswordMismatch
    return UserModel(**switch_id_to_pydantic(user))


async def create_tasks_db() -> None:
    """Create the tasks database."""
    await client.drop_database("tasks")

    tasks_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["title", "description", "completed", "created_at"],
            "properties": {
                "title": {
                    "bsonType": "string",
                    "description": "must be a string. Title of the task",
                },
                "description": {
                    "bsonType": "string",
                    "description": "must be a string. Description of the task",
                },
                "completed": {
                    "bsonType": "bool",
                    "description": "must be a boolean. Completion status of the task",
                },
                "created_at": {
                    "bsonType": "double",
                    "description": "must be a unix timestamp. Creation timestamp of the task",
                },
            },
        },
    }

    await users_db.create_collection("tasks")

    await users_db.command("collMod", "tasks", validator=tasks_validator)

    await users_db.tasks.create_index("title")


class TaskModel(BaseModel):
    """Task model for Pydantic validation."""

    id: ObjectId
    title: str
    description: str
    completed: bool
    created_at: float
    model_config = {"arbitrary_types_allowed": True}


async def get_all_tasks() -> list[TaskModel]:
    """Get all tasks from the database."""
    tasks = await users_db.tasks.find().to_list(100)
    return [TaskModel(**switch_id_to_pydantic(task)) for task in tasks]


async def get_task(id: ObjectId) -> TaskModel:
    """Get a task by its ID."""
    task = await users_db.tasks.find_one({"_id": id})
    if not task:
        raise DBErrors.TaskNotFound
    return TaskModel(**switch_id_to_pydantic(task))


async def create_task(payload: TaskCreate) -> dict[str, str]:
    """Create a new task."""
    try:
        op = await users_db.tasks.insert_one(payload.model_dump())
    except errors.DuplicateKeyError as e:
        raise DBErrors.TaskExists from e
    return {"task_id": str(op.inserted_id)}


async def update_task(_id: ObjectId, payload: TaskUpdate) -> TaskModel:
    """Update an existing task."""
    try:
        await users_db.tasks.update_one(
            {"_id": _id},
            {"$set": payload.model_dump(exclude_unset=True)},
        )
    except Exception as e:
        raise DBErrors.TaskNotFound from e
    return await get_task(_id)


async def delete_task(_id: ObjectId) -> None:
    """Delete a task by its ID."""
    result = await users_db.tasks.delete_one({"_id": _id})
    if result.deleted_count == 0:
        raise DBErrors.TaskNotFound
