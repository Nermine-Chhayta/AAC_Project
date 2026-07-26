# Prompt Log

For each feature, this log captures key prompts used, what the AI returned,
and what was accepted, edited, or rejected. This is a representative sample
of the workflow, not every prompt used.

---

## Feature 1: Due Dates + Overdue Filter

### Prompt 1 — Initial backend implementation (plan-first)
**Exact prompt used:**
> # Task: Implement Feature 1 — Due Dates + Overdue Filter (Backend Only)
>
> ## Context
> This is a Python/FastAPI Task Tracker API. Task fields today: id, title, description,
> status, priority, assignee.
> - Status values: ToDo, InProgress, Done
> - Priority values: Low, Medium, High
>
> I need you to add due date support and overdue detection to the backend only
> (no frontend changes in this task).
>
> ## Process — follow these two phases in order
> **Phase 1: Plan first.** Before writing any code, respond with a concise implementation
> plan covering:
> - Data model changes (new field(s), type, nullability, default)
> - Any migration/schema changes needed (if using a DB) or in-memory model changes
> - Pydantic schema changes (create, update, response models) including validation rules
> - How you'll represent "overdue" — as a computed/derived field vs. a stored field, and why
> - New/changed API endpoints or query parameters (e.g. filtering by overdue)
> - Edge cases you'll handle (no due date, due date removed, due date changed to future,
>   status = Done, invalid date format)
> - Any existing tests or files you expect to touch
>
> Stop after the plan and wait for me to confirm before writing code.
>
> **Phase 2: Implement.** Once I confirm the plan, implement it fully, including tests.
>
> [Functional Requirements — Stories 1-4 — and Technical Notes as specified]
>
> Now start with Phase 1 — the plan.

**AI returned:** A plan proposing `due_date` as an optional field, overdue
computed at request time (not stored) from `due_date` + `status`, and a new
`overdue` query parameter for filtering.

**Decision:** **Accepted** as-is. The "computed, not stored" approach was
exactly right for satisfying the requirement that overdue status updates
automatically when a due date changes — confirmed and moved to implementation.

---

### Prompt 2 — Weak prompt rewritten into a stronger prompt
**Weak prompt (as originally written):**
> great let's implement the plan without changing the older code just implementing the feature

This was vague about what "older code" meant — don't touch existing files at
all? Don't change behavior? Don't refactor while editing?

**Improved prompt used:**
> ## Constraint: Additive implementation only
>
> Implement this feature additively. Specifically:
>
> - Do NOT modify the existing behavior, response shape, or validation logic of any
>   current endpoint beyond what's strictly required to add due_date support.
> - Do NOT rename, restructure, or refactor existing fields, functions, models, or
>   files "while you're in there." If you see something you'd normally clean up,
>   leave it alone and flag it separately instead of changing it.
> - It's expected and fine to EDIT existing files (e.g. the Task model, the Pydantic
>   schemas, the router) to add the new due_date field and overdue logic — that's
>   unavoidable. What you must NOT do is change unrelated code in those same files.
> - Existing API consumers/tests that don't reference due_date should continue to
>   pass unchanged. If any existing test would break because of your change, stop
>   and tell me why instead of editing the test to make it pass.
> - New logic (overdue computation, filtering) should be added as new functions/
>   parameters rather than folded into or replacing existing ones, unless there's
>   no reasonable way to do it additively — in which case, flag it in your plan
>   before implementing.
>
> If following this constraint would require touching something outside the scope
> of due dates/overdue (e.g. a bug you noticed elsewhere), call it out in the plan
> instead of fixing it.

**AI returned:** Implemented due dates and overdue logic touching only the
necessary files, left all existing behavior untouched, and passed the full
existing test suite plus new tests (22 passed).

**Decision:** **Accepted.** This is the clearest example in the whole project
of a vague instruction creating ambiguity risk, versus an explicit constraint
producing a clean, verifiable result.

---

### Prompt 3 — Bug fix: completed indicator not clearing
**Exact prompt used:**
> # Bug Fix: Completed indicator not cleared when status changes away from Done
>
> ## Issue
> When a task's status is changed from Done back to ToDo or InProgress, the
> "Completed" indicator remains on the card instead of being removed. The
> overdue/completed state isn't being recalculated after a status change —
> it looks like it's either being cached from the previous render, or the
> update flow isn't re-deriving the indicator from the task's current
> status + due_date after the API response comes back.
>
> ## Constraint: Additive/targeted fix only
> - Do NOT modify backend code — confirm first whether this is a frontend
>   bug (stale UI state) or backend bug (API not returning updated status/
>   overdue fields correctly on update) before touching anything.
> - Fix only the logic that determines/renders the overdue vs. completed
>   indicator. Do not change any other rendering logic, styling, or
>   unrelated code.
> - Do not change the due_date/overdue/completed logic for any other case
>   that's already working correctly (e.g. ToDo → overdue, InProgress →
>   overdue, Done with past due date → completed).
>
> ## Process
> 1. First, diagnose and tell me the root cause: is the API returning stale/
>    incorrect data after the status update, or is the frontend not re-
>    rendering the card's indicator based on the fresh API response?
> 2. Propose a minimal fix (plan only, no code yet).
> 3. Once I confirm, implement the fix.
>
> [Expected behavior and Verification checklist as specified]
>
> Now start with step 1 — diagnose the root cause.

**AI returned:** Diagnosed that the derived overdue/completed state wasn't
being recalculated after a status change, and proposed a minimal fix to
re-derive the indicator from current status + due_date on every render.

**Decision:** **Accepted** the diagnosis and fix after reviewing that it
correctly explained the root cause rather than just patching the symptom.
Verified manually by toggling status back and forth multiple times.

---

## Feature 2: Search + Combined Filters

### Prompt 1 — Initial backend implementation (plan-first)
**Exact prompt used:**
> # Task: Implement Feature 2 — Search + Combined Filters (Backend Only)
>
> ## Context
> Python/FastAPI Task Tracker API. Task fields: id, title, description, status,
> priority, assignee, due_date (added in Feature 1, already implemented and tested).
> - Status values: ToDo, InProgress, Done
> - Priority values: Low, Medium, High
> - Assignee: free-text string field (no fixed enum)
>
> Extend GET /tasks to support text search and combinable filters: status, priority,
> and assignee. No frontend changes in this task.
>
> ## Constraint: Additive implementation only
> - Do NOT modify existing endpoint behavior for requests that don't use the new
>   search/filter query parameters — GET /tasks with no params must return exactly
>   what it returns today.
> - Do NOT modify Feature 1 (due date/overdue) logic or tests.
> - Do NOT restructure existing files beyond what's needed to add query parameters
>   and filtering logic.
> - If any existing test would break, stop and tell me why instead of editing the
>   test to make it pass.
>
> [Phase 1 plan requirements, Functional Requirements Stories 1-6, and Technical
> Notes as specified — including: search = case-insensitive substring on
> title/description; assignee = case-insensitive EXACT match, not substring;
> empty/missing assignee = no filter applied; validation (422) happens before
> matching logic]
>
> Now start with Phase 1 — the plan.

**AI returned:** A plan matching all specified rules, plus test coverage for
each filter alone, combined, no-match cases, invalid enum values, and a
regression check that `GET /tasks` with no params was unchanged.

**Decision:** **Accepted.** Confirmed and implemented — verified with
`pytest`: 41/41 passing across the full suite.

---

### Prompt 2 — Bug fix: search (`q`) not returning matches
**Exact prompt used:**
> # Bug Fix: Search by title/description not working
>
> ## Issue
> Search input in the filter bar doesn't return matching results when typing text
> that matches a task's title or description. Other filters (status, priority,
> assignee) work correctly. Only the search (`q`) filter is broken.
>
> ## Constraint: Additive/targeted fix only
> - Do NOT modify backend code yet — first diagnose whether this is a frontend
>   bug (not sending `q` correctly, debounce/event issue, param name mismatch) or
>   a backend bug (search matching logic not working as expected), then tell me
>   which it is before touching anything.
> - Fix only the search-related code. Do not change status/priority/assignee
>   filter logic, which is already working correctly.
> - Do not change any other rendering, layout, or unrelated code.
>
> ## Process
> 1. Diagnose and tell me the root cause. Specifically check:
>    - Is the search input actually triggering a fetch (debounce timer firing,
>      event listener attached)?
>    - Is the `q` query param being included in the URL sent to the API, with
>      the correct param name expected by the backend?
>    - Is the fetch being made against the right endpoint/base URL?
>    - If frontend looks correct, test the backend directly (e.g. curl or browser
>      to `/tasks?q=<term>`) to confirm whether the backend itself returns correct
>      results — this isolates frontend vs backend.
>    - If combining search with other active filters, confirm `q` isn't being
>      dropped or overwritten when combined with status/priority/assignee params.
> 2. Propose a minimal fix (plan only, no code yet).
> 3. Once I confirm, implement the fix.
>
> [Expected behavior and Verification checklist as specified]
>
> Now start with step 1 — diagnose the root cause.

**AI returned:** Diagnosed that the frontend code was correct (event listener,
debounce, and `q` param were all wired properly), but the *locally running*
backend process was stale and hadn't reloaded the source that already
contained `q` and `assignee` support — confirmed via a live OpenAPI schema
check showing `q`/`assignee` missing from the running server despite being
present in `app/main.py`.

**Decision:** **Accepted** the diagnosis, and specifically **rejected editing
any frontend code** — restarted the backend process instead. This was a case
where the "diagnose before fixing" instruction directly prevented a wrong fix.

---

### Prompt 3 — Design decision: assignee filter, free text vs. dropdown
**Exact prompt used:**
> free text works fine — just goes against the exact-match backend decision a bit, so worth knowing the trade-off before you lock it in.
>
> [followed up with:] suggesr the better option

**AI returned:** Recommended a dropdown populated from the full unfiltered
task list, reasoning that it stays consistent with the backend's exact-match
decision, removes typo/casing/whitespace failure modes entirely, and costs
almost nothing extra since the task list is already available client-side.

**Decision:** **Accepted** the dropdown recommendation over free text — a
case where thinking through the tradeoff before prompting Copilot avoided
rework in the frontend implementation.