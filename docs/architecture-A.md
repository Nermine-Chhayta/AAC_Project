# Task Tracker Architecture

## What The App Does

Task Tracker is a small FastAPI-backed Kanban task board. Users can create, view, filter, edit, drag between statuses, and delete tasks through a single-page frontend served by the API.

## Data Model

Primary entity: `Task`. Important fields are `id`, `title`, `description`, `status`, `priority`, `assignee`, `due_date`, `task_state`, `created_at`, and `updated_at`. Status values are `ToDo`, `InProgress`, and `Done`; priority values are `Low`, `Medium`, and `High`. `task_state` is computed as `active`, `overdue`, or `completed`.

## Request Flow

When a user creates a task, the frontend collects form values and sends `POST /tasks` to the FastAPI backend. FastAPI validates the payload with `TaskCreate`, rejects unknown or invalid fields with 422 errors, then calls storage to generate a UUID, timestamps, default values, and computed `task_state`. The created task is stored in memory and returned as a `TaskResponse`; the frontend refreshes the board.

## Key Files

- `app/main.py`: FastAPI app setup, CORS, frontend serving, and task route handlers.
- `app/models.py`: Pydantic task schemas, enums, title validation, and task-state computation.
- `app/storage.py`: In-memory task store and CRUD/filtering behavior.
- `app/business_rules.py`: Allowed task status transitions and 422 rejection logic.
- `frontend/index.html`: Single-page Kanban UI, filters, modal form, fetch calls, and drag/drop updates.
- `app/routes/health.py`: `/health` endpoint.
- `app/config.py`: `.env` loading and app settings.
- `tests/test_tasks.py`: API behavior and validation coverage.
- `tests/conftest.py`: Test client and storage reset fixtures.

## Conventions

Validation is handled mainly by Pydantic models: required title, stripped nonblank title, max title length, enum values, date parsing, and forbidden extra fields. Storage is currently a module-level in-memory dictionary, despite README wording about JSON file storage. Missing tasks return 404; validation and invalid status transitions return 422. The frontend talks to `http://127.0.0.1:8000`, uses JSON over REST, refreshes from `/tasks`, and handles server rejection messages for form saves and drag/drop moves.

## Not Visible Or Assumptions

No persistent JSON storage implementation was confirmed. No authentication, authorization, database, migration layer, or deployment-specific production configuration was visible. The architecture assumes one running API process owns the in-memory task state, so data is lost when the process restarts.
