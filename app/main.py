# Entry point for the Task Tracker API.
# Creates the FastAPI application, loads configuration, and registers routes.

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from app import storage
from app.business_rules import validate_status_transition
from app.config import PORT, APP_ENV
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from app.routes.health import router as health_router
from uuid import UUID


app = FastAPI(
    title="Task Tracker API",
    description="A lightweight REST API for tracking tasks, backed by JSON file storage.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the health check route
app.include_router(health_router)

@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    """Return the frontend HTML entrypoint.

    Returns:
        FileResponse: A response serving the `frontend/index.html` file.

    Raises:
        FileNotFoundError: If the frontend file cannot be found.

    Example:
        GET /
    """
    frontend_path = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
    return FileResponse(frontend_path)

@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate):
    """Update an existing task with new values.

    Args:
        task_id: The UUID string of the task to update.
        payload: The partial task payload containing fields to change.

    Returns:
        TaskResponse: The updated task document.

    Raises:
        HTTPException: If the task does not exist.
        HTTPException: If the requested status change is invalid.

    Example:
        PATCH /tasks/{task_id}
        {
            "status": "InProgress",
            "assignee": "alice"
        }
    """
    existing_task = storage.get_task_by_id(task_id)

    if existing_task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    if payload.status is not None and payload.status != existing_task.status:
        validate_status_transition(existing_task.status, payload.status)

    updated_task = storage.update_task(task_id, payload)

    if updated_task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    return updated_task

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    q: str | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee: str | None = None,
    overdue: bool | None = None,
) -> list[TaskResponse]:
    """Return tasks filtered by optional query parameters.

    Args:
        q: Optional search text to match against title and description.
        status: Optional task status to filter by.
        priority: Optional task priority to filter by.
        assignee: Optional assignee name to filter by exact match.
        overdue: Optional overdue flag to filter by overdue state.

    Returns:
        list[TaskResponse]: A list of matching task objects.

    Example:
        GET /tasks?q=report&status=ToDo&overdue=false
    """
    return storage.get_all_tasks(
        q=q,
        status=status,
        priority=priority,
        assignee=assignee,
        overdue=overdue,
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Fetch a single task by its ID.

    Args:
        task_id: The UUID string of the requested task.

    Returns:
        TaskResponse: The requested task.

    Raises:
        HTTPException: If no task exists with the given ID.

    Example:
        GET /tasks/{task_id}
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by ID.

    Args:
        task_id: The UUID string of the task to delete.

    Returns:
        None

    Raises:
        HTTPException: If no task exists with the given ID.

    Example:
        DELETE /tasks/{task_id}
    """
    if storage.delete_task(task_id):
        return None

    raise HTTPException(
        status_code=404,
        detail=f"Task with id {task_id} not found",
    )


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task from the provided payload.

    Args:
        payload: The task creation request body.

    Returns:
        TaskResponse: The newly created task.

    Example:
        POST /tasks
        {
            "title": "Write docstrings",
            "description": "Add documentation for API routes",
            "priority": "Medium",
            "assignee": "bob"
        }
    """
    return storage.add_task(payload)

if __name__ == "__main__":
    # Allows running the app directly with `python app/main.py`
    # in addition to running it via the uvicorn CLI
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=(APP_ENV == "development"),
    )
