# architecture-C.md (draft)

## 1. What the app does
Task Tracker is a lightweight FastAPI service that exposes a REST API for creating, listing, retrieving, updating, and deleting tasks. It also serves a frontend HTML entrypoint at `/`, and it validates task payloads before persisting them into in-memory storage.

## 2. Data model
- `TaskResponse`
  - `id`: string UUID
  - `title`: normalized non-empty string
  - `description`: string
  - `status`: enum `TaskStatus` (`ToDo`, `InProgress`, `Done`)
  - `priority`: enum `TaskPriority` (`Low`, `Medium`, `High`)
  - `assignee`: optional string
  - `due_date`: optional date
  - `task_state`: string derived from status/due date (`completed`, `overdue`, `active`)
  - `created_at`: UTC datetime
  - `updated_at`: UTC datetime
- `TaskCreate`
  - request model for creation
  - same core fields as `TaskResponse` except metadata and `id`
- `TaskUpdate`
  - partial update model
  - all fields optional for PATCH

## 3. Request flow: creating a task
1. Client sends `POST /tasks` with a `TaskCreate` JSON payload.
2. FastAPI validates the payload against `TaskCreate`.
3. `app.storage.add_task()` generates a UUID and timestamps, computes `task_state`, and constructs a `TaskResponse`.
4. The task is stored in the in-memory `_tasks` dict.
5. The created `TaskResponse` is returned with HTTP `201 Created`.

## 4. Key files
- `app/main.py` — FastAPI app, CORS setup, route definitions, frontend entrypoint.
- `app/models.py` — Pydantic request/response models, enums, title validation, task state logic.
- `app/storage.py` — in-memory task persistence and filters for list/get/update/delete.
- `app/business_rules.py` — referenced for status transition validation but not read.
- `app/config.py` — referenced for runtime port/env values but not read.
- `app/routes/health.py` — health route included by `main.py` but not read.
- `frontend/index.html` — served by root route but not read.
- `tests/test_tasks.py` — likely validates API behavior but not read.
- `requirements.txt` — dependency list implied by imports but not read.
- `README.md` — project overview implied but not read.

## 5. Conventions
- Validation
  - `TaskCreate` and `TaskUpdate` use `extra="forbid"` to reject unknown fields.
  - Titles are stripped, required for create, and limited to 200 characters.
  - `TaskUpdate` allows `None` values and only validates title when provided.
- Storage
  - Tasks are stored in-memory in `_tasks: dict[str, TaskResponse]`.
  - No durable JSON file persistence is visible here, despite the app description.
- Error handling
  - `get`, `patch`, and `delete` return `404` via `HTTPException` when tasks are missing.
  - Invalid status transitions are checked before update, but the transition rules themselves are not visible in these files.
- Frontend/backend interaction
  - `/` serves `frontend/index.html`.
  - API surface includes `GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PATCH /tasks/{id}`, `DELETE /tasks/{id}`.

## 6. Not visible or assumptions
- Not visible from the files I read: the actual status transition rules in `app.business_rules`.
- Not visible from the files I read: whether storage is persisted to JSON or durable storage.
- Not visible from the files I read: frontend UI behavior and exact request payloads beyond the API contract.
- Not visible from the files I read: health route implementation details.
- Not visible from the files I read: runtime configuration values from `app.config` beyond the imported names.

---

Files read:
- `app/main.py`
- `app/models.py`
- `app/storage.py`

What this targeted strategy likely missed:
- business-rule logic for allowed status updates
- config/environment handling
- health route and any non-task API endpoints
- frontend implementation and client-side behavior
- documentation, tests, and deployment details
