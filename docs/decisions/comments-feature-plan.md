# Comments On Tasks Feature Plan

This document plans a comments feature for the Task Tracker repository without implementing it. It is based on the current FastAPI, Pydantic, in-memory storage, pytest, and single-page frontend patterns observed in the repository.

## 1. Data Model

Comments should follow the model conventions already used in `app/models.py`: Pydantic v2 `BaseModel` classes, `ConfigDict(extra="forbid")`, server-generated identifiers, and timezone-aware UTC timestamps.

Recommended models:

| Model | Purpose | Fields |
| --- | --- | --- |
| `CommentCreate` | Request body for creating a comment on a task. | `author`, `body` |
| `CommentResponse` | Response body for comment reads and creates. | `id`, `task_id`, `author`, `body`, `created_at` |

The comment models belong in `app/models.py` if the project keeps the current pattern of task models and API models in one module. A future split could move task and comment schemas into `app/schemas/`, but the visible task API currently imports `TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskStatus`, and `TaskPriority` from `app/models.py`, while `app/schemas/` is only used for the health response.

Validation should mirror the existing title validation style:

| Field | Validation |
| --- | --- |
| `author` | Required string, trim surrounding whitespace, reject blank values, reject values longer than 100 characters. |
| `body` | Required string, trim surrounding whitespace or at least reject whitespace-only values, reject values longer than 2000 characters. |
| `id` | Server-generated UUID string; clients cannot set it. |
| `task_id` | Server-assigned from the route path, not accepted in the create request body. |
| `created_at` | Server-generated timezone-aware UTC datetime; clients cannot set it. |

Storage should fit the visible `app/storage.py` approach. The current task store is an in-memory `_tasks: dict[str, TaskResponse]`, with helper functions such as `add_task`, `get_all_tasks`, `get_task_by_id`, `update_task`, `delete_task`, and `_reset`. A comments implementation could add an in-memory `_comments: dict[str, CommentResponse]` plus helper functions for creating, listing, fetching, and deleting comments.

For lookup efficiency and simpler deletion behavior, comments can be stored either as one flat dictionary keyed by comment id with filtering by `task_id`, or as `dict[str, list[CommentResponse]]` keyed by task id. A flat dictionary better matches the current `_tasks` shape and makes individual comment ids globally unique.

Task responses should not include embedded comments by default. The existing `GET /tasks` endpoint returns lightweight task cards and supports board filtering. Adding comments into every task response would change the frontend contract and increase response size for the board. Prefer separate nested comment routes.

## 2. API Routes

Routes should be added alongside the existing task routes in `app/main.py` unless the project first introduces an `app/routes/tasks.py` router. The current code defines task routes directly in `app/main.py` and includes only the health router from `app/routes/health.py`.

| Method | Path | Request Body | Response Body | Success |
| --- | --- | --- | --- | --- |
| `POST` | `/tasks/{task_id}/comments` | `CommentCreate` with `author` and `body` | `CommentResponse` | `201 Created` |
| `GET` | `/tasks/{task_id}/comments` | None | List of `CommentResponse` | `200 OK` |
| `GET` | `/tasks/{task_id}/comments/{comment_id}` | None | `CommentResponse` | `200 OK` |
| `DELETE` | `/tasks/{task_id}/comments/{comment_id}` | None | Empty body | `204 No Content` |

Creation behavior:

- First verify the parent task exists using the same missing-task convention as `GET /tasks/{task_id}`.
- Generate a UUID string for the comment id.
- Set `task_id` from the route path.
- Set `created_at` using the same timezone-aware UTC pattern used by `app/storage.py`.
- Return the created comment with HTTP 201.

Listing behavior:

- Return comments for the task in creation order, oldest first, unless the team chooses a different UI order.
- Return an empty list when the task exists but has no comments.
- Return 404 when the parent task does not exist.

Fetching behavior:

- Return the comment only when both the task and comment exist and the comment belongs to that task.
- Return 404 when the parent task does not exist.
- Return 404 when the comment does not exist under that task.

Deletion behavior:

- Return 204 and an empty body when deleting an existing comment.
- Return 404 when the parent task does not exist.
- Return 404 when the comment does not exist under that task.

Error cases should match current FastAPI and repository conventions:

| Case | Expected Status | Notes |
| --- | --- | --- |
| Parent task id not found | `404` | Current task routes use detail text like `Task with id {task_id} not found`. |
| Comment id not found for a task | `404` | Use a clear detail such as comment not found for the task. Exact text should be tested once chosen. |
| Missing `author` | `422` | Pydantic validation, like missing task title. |
| Blank or whitespace-only `author` | `422` | Should follow task title behavior. |
| `author` longer than 100 characters | `422` | Required by feature spec. |
| Missing `body` | `422` | Pydantic validation. |
| Blank or whitespace-only `body` | `422` | Required string should not accept empty content. |
| `body` longer than 2000 characters | `422` | Required by feature spec. |
| Unknown create field | `422` | Existing models use `extra="forbid"`. |
| Client-provided `id`, `task_id`, or `created_at` | `422` | Keep server-owned fields out of `CommentCreate`. |

No comment update route is recommended for the first version because the requested comment shape has no `updated_at`, and the feature spec only defines `created_at`.

## 3. Tests

Tests should follow the style in `tests/test_tasks.py`: use the `client` fixture from `tests/conftest.py`, create prerequisite tasks through `POST /tasks`, assert HTTP status codes, and assert response JSON fields directly. The autouse `_reset_storage` fixture currently resets task storage before and after each test, so it would need to reset comments too.

Happy path test names:

- `test_create_comment_for_task_returns_201_with_full_body`
- `test_list_comments_for_task_returns_comments_in_creation_order`
- `test_list_comments_for_task_with_no_comments_returns_empty_list`
- `test_get_comment_by_id_returns_comment`
- `test_delete_existing_comment_returns_204_no_body`
- `test_delete_task_removes_or_hides_its_comments`

Validation test names:

- `test_create_comment_missing_author_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_author_over_100_chars_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_body_over_2000_chars_returns_422`
- `test_create_comment_unknown_field_returns_422`
- `test_create_comment_rejects_client_owned_fields`

Edge case test names:

- `test_create_comment_for_missing_task_returns_404`
- `test_list_comments_for_missing_task_returns_404`
- `test_get_comment_for_missing_task_returns_404`
- `test_get_missing_comment_returns_404`
- `test_get_comment_from_different_task_returns_404`
- `test_delete_comment_for_missing_task_returns_404`
- `test_delete_missing_comment_returns_404`
- `test_delete_comment_from_different_task_returns_404`
- `test_reset_storage_clears_comments_between_tests`

Frontend contract tests could extend `tests/test_frontend_contract.py` with API-level coverage that the frontend depends on:

- `test_frontend_can_create_and_list_task_comments`
- `test_frontend_delete_comment_contract_returns_204`

## 4. Frontend Changes

The visible frontend is entirely in `frontend/index.html`, with embedded HTML, CSS, and JavaScript. No separate frontend build system, component files, or static JS files are visible.

Recommended UI changes in `frontend/index.html`:

- Add a comments affordance to each task card, near the existing `Edit` button in `.task-actions`.
- Show a comment count on the card when comments have been loaded or after a comment is created.
- Add a task detail or comments modal/panel that displays the selected task title plus its comments.
- Include a comment form with `author` and `body`.
- Show validation or server errors using the existing `.form-error` and `.field-error` style patterns.
- Add a delete control per comment if the API includes comment deletion.
- Escape rendered comment `author` and `body` with the existing `escapeHtml` function, since task card rendering already uses string templates.

Expected user experience:

- A user can open comments from a task card.
- The comments area loads comments for that task.
- If there are no comments, the user sees an empty state in the comments area.
- The user can add a comment with an author and body.
- The new comment appears in the list after successful creation.
- The user sees inline errors for missing or invalid author/body values.
- If a task is deleted, comments for that task should no longer be visible through the UI.

API integration points in the existing script:

- Add functions similar to `fetchTasks`, `submitTask`, and `getServerMessage`, but scoped to comments.
- Use the existing `apiBaseUrl = "http://127.0.0.1:8000"`.
- Keep task board loading independent from comment loading so opening comments does not refetch the entire board unless the team intentionally adds comment counts to `GET /tasks`.

## 5. Migration Notes

The current implementation stores tasks in memory in `app/storage.py`; no JSON persistence implementation is visible, despite README and FastAPI metadata text describing JSON file storage. With the current runtime shape, adding comments does not require a data migration because data is lost when the process restarts.

If JSON file storage is later implemented or exists outside the visible files, the storage shape must change to persist comments. The team should choose one of these shapes:

| Shape | Notes |
| --- | --- |
| Separate top-level comments collection | Example conceptual shape: tasks remain separate, comments are keyed by comment id and include `task_id`. This mirrors a relational foreign-key style. |
| Embedded comments under each task | Easier task cleanup, but changes task document size and may complicate list responses. |

If task deletion is implemented with comment cleanup, deleting a task should remove associated comments from storage. If cleanup is not implemented, all comment read routes must filter by existing task ids so orphaned comments are inaccessible.

The storage reset helper `_reset()` in `app/storage.py` should clear both tasks and comments so the existing autouse fixture in `tests/conftest.py` continues to isolate tests.

No migration path for existing persisted task data can be confirmed from the visible repository files because the current storage code is in-memory only.

## 6. Open Questions

- Should comments be editable after creation? The requested data shape has `created_at` but no `updated_at`, so edit support would require expanding the model.
- Should deleting a task cascade-delete comments, retain inaccessible comments, or reject task deletion while comments exist?
- Should comment lists be oldest-first for conversation history or newest-first for recent activity?
- Should `author` be free text as requested, or should it eventually connect to users/accounts?
- Should `body` preserve line breaks and whitespace exactly, or trim the stored value after validation?
- Should `GET /tasks` include comment counts for board cards, or should the frontend fetch counts/comments only when a task is opened?
- Should comments support filtering, pagination, or limits per task, or is an unpaginated list acceptable for this learning app?

## Files read

- `AGENTS.md`
- `README.md`
- `app/models.py`
- `app/main.py`
- `app/storage.py`
- `app/business_rules.py`
- `app/routes/health.py`
- `frontend/index.html`
- `tests/conftest.py`
- `tests/test_tasks.py`
- `tests/test_frontend_contract.py`
- `tests/verify_a.py`

## Assumptions to verify

- Comments should be implemented against the visible in-memory storage layer unless the README's JSON storage claim is later reconciled with code.
- The first version does not need comment editing because no `updated_at` field was requested.
- Comment routes should be nested under tasks and should not alter the existing `TaskResponse` shape by default.
- The frontend should stay as a single-file app in `frontend/index.html` unless a separate frontend refactor is approved.
