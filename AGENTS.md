# AGENTS.md

## Project Summary

This repository contains a Module 5 Task Tracker application: a lightweight FastAPI REST API with a single-page Kanban-style frontend served from `frontend/index.html`.

The API supports creating, listing, filtering, fetching, updating, and deleting tasks. The visible implementation currently stores tasks in an in-memory dictionary in `app/storage.py`. The README describes JSON file storage, but no JSON persistence implementation was confirmed in the inspected code.

## Tech Stack

- Python 3.11 target, based on `Dockerfile`.
- FastAPI API application in `app/main.py`.
- Pydantic v2 models and validation in `app/models.py`.
- In-memory task storage in `app/storage.py`.
- Business-rule validation in `app/business_rules.py`.
- Static HTML/CSS/JavaScript frontend in `frontend/index.html`.
- Pytest tests under `tests/`.
- Environment loading via `python-dotenv` in `app/config.py`.

## Supported Run and Test Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API locally:

```bash
uvicorn app.main:app --reload --port 8000
```

Alternative app entrypoint visible in code:

```bash
python app/main.py
```

Run tests:

```bash
python -m pytest
```

or, when `pytest` is available on PATH:

```bash
pytest
```

Docker support is visible in `Dockerfile`:

```bash
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
```

Notes:

- `pytest.ini` sets `pythonpath = .` and `testpaths = tests`.
- In the current shell, `python`, `py`, and `pytest` were not available on PATH, so test execution was not locally confirmed.
- README references copying `.env.example` to `.env`, but `.env.example` was not present in the inspected file listing.

## Business Rules Visible in Code

Task statuses are defined in `app/models.py`:

- `ToDo`
- `InProgress`
- `Done`

Task priorities are defined in `app/models.py`:

- `Low`
- `Medium`
- `High`

Task creation defaults:

- `status` defaults to `ToDo`.
- `priority` defaults to `Medium`.
- `description` defaults to an empty string.
- `assignee` defaults to `None`.
- `due_date` defaults to `None`.

Validation rules:

- `title` is required on create.
- `title` is stripped of surrounding whitespace.
- blank or whitespace-only titles are rejected.
- titles longer than 200 characters are rejected.
- unknown request fields are rejected because Pydantic models use `extra="forbid"`.
- invalid status, priority, and due date values are rejected by Pydantic/FastAPI with validation errors.
- clients cannot set fields that are not declared on `TaskCreate` or `TaskUpdate`, such as `id`, `created_at`, or `updated_at`.

Task metadata and state:

- task IDs are generated with `uuid4()`.
- `created_at` and `updated_at` use timezone-aware UTC timestamps.
- `task_state` is computed as:
  - `completed` when status is `Done`;
  - `overdue` when there is a due date before today's date and status is not `Done`;
  - `active` otherwise.
- updating a task recomputes `task_state`.
- a PATCH request with no changed fields returns the existing task unchanged.

Allowed status transitions are defined in `app/business_rules.py`:

- `ToDo -> InProgress`
- `InProgress -> Done`
- `Done -> InProgress`
- setting the same status is allowed.

Rejected status transitions return HTTP 422. For example, `ToDo -> Done` is rejected.

API behavior visible in `app/main.py` and tests:

- `GET /` serves `frontend/index.html`.
- `GET /health` is registered from `app/routes/health.py`.
- `POST /tasks` creates a task and returns HTTP 201.
- `GET /tasks` lists tasks.
- `GET /tasks/{task_id}` returns HTTP 404 when the task is missing.
- `PATCH /tasks/{task_id}` updates a task and returns HTTP 404 when the task is missing.
- `DELETE /tasks/{task_id}` returns HTTP 204 for an existing task and HTTP 404 when missing.
- list filters include `q`, `status`, `priority`, `assignee`, and `overdue`.
- `q` searches title and description case-insensitively.
- `assignee` filtering is exact and case-insensitive, not substring-based.
- empty or whitespace-only `q` and `assignee` filters are treated as unfiltered.
- combined filters use AND logic.
- `overdue=true` returns tasks whose `task_state` is `overdue`.

Frontend behavior visible in `frontend/index.html`:

- the frontend uses API base URL `http://127.0.0.1:8000`.
- tasks are displayed in Kanban columns for `ToDo`, `InProgress`, and `Done`.
- cards are sorted by priority order `High`, `Medium`, `Low`, then by task ID.
- the UI supports create, edit, filtering, overdue-only filtering, and drag-and-drop status updates.
- drag-and-drop status updates can be rejected by the backend transition rules.

## Module 5 Guardrails

- Docs-first: inspect README, docs, tests, and relevant source files before making claims or changes.
- Read-only by default: prefer analysis, citations, and proposed changes before editing.
- One task per thread: keep each Codex task focused on one requested outcome.
- Do not modify files under `app/` unless the user explicitly approves that scope.
- For this repository, default to editing documentation only unless the user clearly requests implementation work.

## Security and Governance Reminders

- Do not paste, expose, or invent secrets, tokens, API keys, credentials, or private environment values.
- Do not run destructive commands such as recursive deletes, force resets, or cleanup scripts unless the user explicitly requests them and the target is verified.
- Cite the files that support findings, especially for business rules and supported commands.
- Do not invent findings. If a command, dependency, behavior, or business rule is not visible in the repo, mark it as not confirmed.
- Preserve user work. Do not revert unrelated changes.
- Keep changes tightly scoped to the user request.
