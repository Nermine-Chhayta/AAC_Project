from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskResponse, TaskUpdate, _compute_task_state

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    now = datetime.now(timezone.utc)
    task_id = str(uuid4())
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        task_state=_compute_task_state(payload.status, payload.due_date),
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(q=None, status=None, priority=None, assignee=None, overdue=None) -> list[TaskResponse]:
    tasks = list(_tasks.values())
    search_text = q.strip().casefold() if q is not None else None
    assignee_text = assignee.strip().casefold() if assignee is not None else None

    if search_text:
        tasks = [
            task
            for task in tasks
            if search_text in task.title.casefold()
            or search_text in task.description.casefold()
        ]
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if assignee_text:
        tasks = [
            task
            for task in tasks
            if task.assignee is not None and task.assignee.casefold() == assignee_text
        ]
    if overdue is not None:
        tasks = [task for task in tasks if (task.task_state == "overdue") is overdue]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = _tasks.get(task_id)

    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        return task

    updated_data = task.model_dump()
    updated_data.update(updates)
    updated_data["updated_at"] = datetime.now(timezone.utc)
    updated_data["task_state"] = _compute_task_state(
        updated_data.get("status"),
        updated_data.get("due_date"),
    )

    updated_task = TaskResponse(**updated_data)

    _tasks[task_id] = updated_task

    return updated_task


def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()
