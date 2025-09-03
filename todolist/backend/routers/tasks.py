from fastapi import APIRouter, Depends, Request

from todolist.backend.schemas.tasks import TaskCreate, TaskUpdate
from todolist.backend.utils.database import (
    TaskModel,
    create_task,
    get_all_tasks,
    get_task,
    update_task,
)
from todolist.backend.utils.session import validate_session

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
    dependencies=[Depends(validate_session)],
)


def parse_task(task: TaskModel) -> dict[str, dict]:
    """Parse a task model into a dictionary."""
    return {"id": str(task.id), **task.model_dump()}


@router.get("/")
async def get_tasks(request: Request) -> dict[str, list[dict]]:  # noqa: ARG001
    """Get all tasks."""
    tasks = await get_all_tasks()
    parsed_tasks = [parse_task(task) for task in tasks]
    return {"tasks": parsed_tasks}


@router.get("/{task_id}")
async def get_task_by_id(
    request: Request,  # noqa: ARG001
    task_id: str,
) -> dict[str, dict]:
    """Get a task by its ID."""
    task = await get_task(task_id)
    return {"task": parse_task(task)}


@router.post("/")
async def create_new_task(
    request: Request,  # noqa: ARG001
    payload: TaskCreate,
) -> dict[str, dict]:
    """Create a new task."""
    task = await create_task(payload)
    return {"task": parse_task(task)}


@router.put("/{task_id}")
async def update_existing_task(
    request: Request,  # noqa: ARG001
    task_id: str,
    payload: TaskUpdate,
) -> dict[str, dict]:
    """Update an existing task."""
    task = await update_task(task_id, payload)
    return {"task": parse_task(task)}
