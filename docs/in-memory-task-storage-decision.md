# In-Memory Task Storage Decision Note

## 1. Context

The Module 4 Task Tracker is a lightweight FastAPI application. The API routes in `app/main.py` delegate all task operations to `app.storage`. The task model definitions in `app/models.py` are Pydantic-based and include fields like `id`, `title`, `status`, `priority`, `assignee`, `due_date`, `task_state`, `created_at`, and `updated_at`.

`app/storage.py` implements persistence as a module-level dictionary:

- `_tasks: dict[str, TaskResponse] = {}`
- `add_task()` generates a UUID and timestamps, then stores the task in `_tasks`
- `get_all_tasks()`, `get_task_by_id()`, `update_task()`, and `delete_task()` operate directly on that dict

The Dockerfile and CI workflow are minimal and oriented toward a local Python container and `pytest` execution. There is no current code path for a database, external persistence service, or production hardening.

## 2. Decision

Use in-memory task storage for Module 4, with `app/storage.py` as the single source of truth for task state. This keeps the implementation simple, minimizes dependencies, and aligns with the app’s current lightweight scope. The runtime stores tasks only for the life of the process, and persistence across restarts is intentionally not supported at this stage.

## 3. Alternatives Considered

- File-backed JSON persistence, which is mentioned in `README.md` but is not reflected in the current codebase
- SQLite or another embedded database
- External database service
- A storage abstraction or repository layer to decouple the API from the persistence mechanism

## 4. DRAFT - REWRITE IN MY OWN WORDS

- The in-memory approach is simple and easy to understand, with no extra runtime dependency beyond Python and FastAPI.
- It supports isolated testing and local development well, since state is reset on each process start.
- It does not provide durability, so tasks are lost on restart.
- It does not support multi-instance deployment or concurrent access from multiple processes.
- It means the current implementation is not suitable for any scenario that requires real persistence, but it is acceptable for a learning-focused module and local demo use.
- There is an inconsistency between the README’s claim of JSON file storage and the actual code; that suggests either a documentation drift or an implementation gap [VERIFY].

## 5. Consequences

- Task data exists only in memory while the app is running.
- Restarting the server clears all tasks.
- The current API can still support task creation, query, update, and deletion in a single running process.
- Future changes can replace `app/storage.py` with a different backend without changing the API routes if a storage abstraction is introduced.
- CI and container behavior remain aligned with the current in-memory design, since tests and Docker focus on the code as written.

## 6. DRAFT - REWRITE IN MY OWN WORDS

- Does the app need the JSON file persistence described in `README.md`, or should the docs be updated to reflect in-memory storage?
- Should we introduce a storage abstraction now so the in-memory backend can be swapped later with minimal API change?
- If persistence is required later, what is the simplest durable backend: JSON file, SQLite, or another lightweight store?
- I would do this differently by... introducing a storage interface and a pluggable backend so the application can start with in-memory storage and later move to durable persistence cleanly.
