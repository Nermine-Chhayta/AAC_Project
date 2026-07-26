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
    frontend_path = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
    return FileResponse(frontend_path)

@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate):
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
    return storage.get_all_tasks(
        q=q,
        status=status,
        priority=priority,
        assignee=assignee,
        overdue=overdue,
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    if storage.delete_task(task_id):
        return None

    raise HTTPException(
        status_code=404,
        detail=f"Task with id {task_id} not found",
    )


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
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
