from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status

import todolist.backend.utils.database as db
from todolist.backend.schemas.tasks import TaskCreate, TaskUpdate
from todolist.backend.utils.session import validate_session

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
    dependencies=[Depends(validate_session)],
)


def parse_task(task: db.TaskModel) -> dict[str, dict]:
    """Parse a task model into a dictionary."""
    return {"id": str(task.id), **task.model_dump(exclude={"id"})}


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task(
    request: Request,  # noqa: ARG001
    task_id: str,
) -> dict[str, dict]:
    """Get a task by its ID."""
    try:
        task = await db.get_task(ObjectId(task_id))
        print(task)
        return {"task": parse_task(task)}
    except db.DBErrors.TaskNotFound as e:
        raise HTTPException(status_code=404, detail="Task not found") from e


@router.get("/", status_code=status.HTTP_200_OK)
async def get_tasks(request: Request) -> dict[str, list[dict]]:  # noqa: ARG001
    """Get all tasks."""
    tasks = await db.get_all_tasks()
    parsed_tasks = [parse_task(task) for task in tasks]
    return {"tasks": parsed_tasks}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,  # noqa: ARG001
    payload: TaskCreate,
) -> dict[str, str]:
    """Create a new task."""
    try:
        op = await db.create_task(payload)
    except db.DBErrors.TaskExists as e:
        raise HTTPException(status_code=400, detail="Task already exists") from e
    return op


@router.patch("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    request: Request,  # noqa: ARG001
    task_id: str,
    payload: TaskUpdate,
) -> dict[str, dict]:
    """Update an existing task."""
    try:
        task = await db.update_task(ObjectId(task_id), payload)
    except db.DBErrors.TaskNotFound as e:
        raise HTTPException(status_code=404, detail="Task not found") from e
    return {"task": parse_task(task)}


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    request: Request,  # noqa: ARG001
    task_id: str,
) -> None:
    """Delete an existing task."""
    await db.delete_task(ObjectId(task_id))
