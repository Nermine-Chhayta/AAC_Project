# Architecture B: Task Tracker App

## What The App Does

Task Tracker is a lightweight FastAPI application with a single-page Kanban frontend. It lets users create, view, filter, update, move, and delete tasks across `ToDo`, `InProgress`, and `Done` columns, with backend validation enforcing task rules and status transitions.

## Data Model

The main entity is a task. Important fields include `id`, `title`, `description`, `status`, `priority`, `assignee`, `due_date`, `created_at`, `updated_at`, and computed `task_state`.

Supported statuses are `ToDo`, `InProgress`, and `Done`. Supported priorities are `Low`, `Medium`, and `High`. `task_state` is computed as `completed` for done tasks, `overdue` for unfinished tasks past their due date, and `active` otherwise.

## Request Flow

When a user creates a task from the frontend, `frontend/index.html` sends a request to the FastAPI backend at `POST /tasks`. The backend validates the request with the Pydantic task creation model, rejects unsupported or invalid fields, applies defaults such as `ToDo` status and `Medium` priority, generates metadata such as `id`, `created_at`, and `updated_at`, computes task state, stores the task in the in-memory storage layer, and returns the created task with HTTP 201.

## Key Files

- `app/main.py` - FastAPI app entrypoint and task API routes.
- `app/models.py` - Pydantic models, task fields, statuses, priorities, and validation.
- `app/storage.py` - in-memory task storage implementation.
- `app/business_rules.py` - allowed task status transitions and business validation.
- `app/routes/health.py` - health check route.
- `frontend/index.html` - single-page Kanban UI and frontend API interaction.
- `tests/test_tasks.py` - API behavior tests for task operations.
- `tests/test_frontend_contract.py` - frontend/API contract tests.
- `README.md` - project overview and run/test instructions.
- `Dockerfile` - container build and runtime setup.

## Conventions

Task titles are required, trimmed, limited to 200 characters, and cannot be blank. Unknown request fields are rejected. Invalid status, priority, and due date values are rejected by FastAPI/Pydantic validation.

Tasks are currently stored in an in-memory dictionary. Task IDs are generated with `uuid4()`, and timestamps are timezone-aware UTC values.

Status transitions are restricted: `ToDo -> InProgress`, `InProgress -> Done`, and `Done -> InProgress` are allowed, as is setting the same status. Invalid transitions return HTTP 422. Missing tasks return HTTP 404. Delete returns HTTP 204 for existing tasks.

The frontend talks to the backend using `http://127.0.0.1:8000`, displays tasks in Kanban columns, sorts cards by priority and task ID, supports filtering, and handles backend rejection of invalid drag-and-drop status changes.

## Not Visible Or Assumptions

README documentation reportedly describes JSON file storage, but the structured context confirms only in-memory storage in `app/storage.py`. No JSON persistence implementation is confirmed here.

Test execution was not locally confirmed in the provided context because `python`, `py`, and `pytest` were reported unavailable on PATH.

No behavior beyond the listed files, summaries, AGENTS.md content, and provided project context is assumed.
