# Decision Note — Due Dates + Overdue Filter & Search + Combined Filters

## Process
For both features, I followed the workflow taught in the course: started by
writing user stories and acceptance criteria with ChatGPT, then manually
inspected and edited them for clarity and correctness before moving on to
implementation. For example, Story 3 in Feature 1 was tightened to make it
explicit that tasks with status Done display a completed indicator instead of
an overdue indicator, rather than just implying it. Similarly, Story 6 in
Feature 2 (assignee filtering) was added after implementation started, once it
became clear the feature description mentioned assignee as a combinable filter
but the original user stories hadn't covered it.

Claude was used to turn the finalized user stories for each feature into
structured, constrained implementation prompts — including explicit plan-first
instructions, relevant project context, and additive-only constraints to avoid
unintended changes to existing working code. Claude was also used to reason
through smaller design decisions before they were written into prompts, such as
whether the assignee filter should be free text or a dropdown, and whether it
should require exact or partial matching.

GitHub Copilot (VS Code, agent mode) generated the actual code in the project
environment for both features, covering backend (FastAPI) and frontend (vanilla
HTML/CSS/JS) work as needed.

## Practices followed (both features)
- AI was always asked to produce a plan first and wait for confirmation before
  writing any code, both for initial implementation and for later bug fixes.
- Prompts always included explicit context (existing schema, field constraints,
  what had already been built) and explicit constraints (additive-only, don't
  modify unrelated code, don't cross backend/frontend boundaries unnecessarily).
- Every generated change was verified before being accepted: backend via
  `pytest`, frontend by running the app locally and manually checking each
  acceptance criterion in the browser.

## Feature 1: Due Dates + Overdue Filter
### Implementation decisions
- Overdue status is computed at request time from `due_date` + `status` rather
  than stored as a field, so it can't go stale when a date or status changes.
- Completed and overdue are treated as mutually exclusive derived states, so the
  UI never shows both indicators at once.

### Alternatives suggested and rejected
- AI suggested storing an `is_overdue` boolean on the task, updated on every
  write. Rejected as unnecessary complexity for this scope — a computed value
  achieves the same acceptance criteria with less state to keep in sync.
- AI suggested a general-purpose date utility module. Rejected as out of scope —
  broader than what the user stories required.

### Bug fix
After testing, found that moving a task from Done back to InProgress left the
"Completed" indicator visible. AI was asked to diagnose the root cause and
propose a plan before making any change; the plan was reviewed and confirmed
before the fix was applied.

## Feature 2: Search + Combined Filters
### Implementation decisions
- `q` performs a case-insensitive substring match across title and description,
  while `status` and `priority` remain strictly validated enum filters (invalid
  values return 422), consistent with existing validation patterns in the app.
- Assignee filtering uses a case-insensitive **exact** match rather than
  substring matching, since assignee represents a small, known set of team
  members rather than free-form text — this was decided explicitly to avoid
  ambiguous partial matches (e.g. "Jo" matching both "John" and "Joanna").
- On the frontend, assignee is implemented as a dropdown (not a free-text
  input), populated from the full unfiltered task list rather than the
  currently filtered view, so the option list never shrinks as other filters
  are applied. This choice was made specifically to stay consistent with the
  backend's exact-match decision — a dropdown guarantees every selectable value
  actually exists and will return results, whereas free text risked silent
  empty results from typos or casing/whitespace mismatches.
- All active filters (search, status, priority, assignee) combine using AND
  logic, sent together as query parameters, with columns and their empty
  states always kept visible rather than hidden when a filter yields no
  matches.

### Alternatives suggested and rejected
- AI suggested making the assignee filter a free-text input for simplicity.
  Rejected in favor of a dropdown after weighing the trade-off — a dropdown
  removes an entire class of user-facing bugs (typos, case mismatches, stray
  whitespace) for negligible extra implementation cost, since the distinct
  assignee list can be derived client-side from data already being fetched.
- AI suggested substring matching for the assignee filter, mirroring the
  search field. Rejected as inconsistent with treating assignee as a
  categorical filter rather than free-text search, and because it would
  produce ambiguous matches between similarly-named assignees.
- Considered adding enum-style validation (422) for assignee, mirroring status
  and priority. Rejected as out of scope — assignee has no fixed enum in the
  data model, so an unrecognized value is a legitimate "no results" case, not
  an invalid request.

### Bug fix / issues found
After implementation, the search (`q`) filter appeared broken in the browser
while status/priority/assignee filters worked correctly. AI was asked to
diagnose before making changes rather than immediately editing code. Diagnosis
found the frontend code was correct, but the locally running backend process
was stale and hadn't reloaded the updated `app/main.py`, so the live API didn't
actually expose the `q` parameter yet despite it being present in source. This
was resolved by restarting the backend rather than changing any code — a good
example of confirming root cause before applying a fix, since editing the
frontend based on the symptom alone would have been the wrong fix entirely.