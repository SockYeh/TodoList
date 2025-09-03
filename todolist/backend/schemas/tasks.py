from time import time

from pydantic import BaseModel


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str
    description: str
    completed: bool
    created_at: float = time()


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    id: int
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
