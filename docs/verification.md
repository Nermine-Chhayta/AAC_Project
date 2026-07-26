# Verification Log

This document records the baseline check, backend test results, manual browser verification, the preserved behavior contract before/after each feature, and evidence of deliberate "break tests" — cases where a known-bad input or edge scenario was checked to confirm the system correctly rejects or handles it, not just that the happy path works.

## Baseline Check

Before implementing Feature 1, the existing test suite was run to confirm the starting state of the project (CRUD endpoints for tasks; status/priority enum validation) was fully passing, with no due-date, search, or filter logic yet present. This baseline is the reference point for the "additive only" constraint used in every implementation prompt — any regression against it would indicate existing functionality had been broken.

Command run: `python -m pytest -q test_tasks.py`. Baseline result: all existing tests passing prior to any Feature 1 or Feature 2 changes.

## Feature 1: Due Dates + Overdue Filter

### Backend test results

Command run: `python -m pytest -q test_tasks.py`. Result: 22 passed in 0.30s.

This confirmed: `due_date` accepted as optional on task creation; `due_date` saved and returned correctly when provided; `due_date` can be added, changed, or cleared via update; invalid date formats correctly return HTTP 422; overdue correctly computed from `due_date` + `status` (past date and status not Done → overdue); tasks without a `due_date` are never marked overdue; tasks with status Done show a "completed" indicator instead of "overdue," even with a past due date; and `GET /tasks?overdue=true` returns only overdue tasks, excluding tasks with no due date.

### Manual browser checks

Created a task with a future due date and confirmed it displayed on the card with no overdue indicator. Created a task with a past due date and status not Done, and confirmed the "Overdue" indicator appeared on the card. Edited a task's due date from past to future and confirmed the overdue indicator disappeared immediately after update. Moved an overdue task to Done and confirmed "Completed" replaced "Overdue" on the card. Confirmed a task with no due date never showed a due date field or an overdue indicator, in any status.

### Behavior contract — before / after

Before: `GET /tasks` returned task objects with id, title, description, status, priority, and assignee. After: `GET /tasks` returns the same fields plus a nullable `due_date` and a derived overdue/completed indicator, with existing fields unchanged in shape or behavior, and requests that don't reference `due_date` behaving identically to before the feature was added.

### Break Test evidence

**Test 1 — Invalid date format rejected.** Submitted a `due_date` in a non-ISO-8601 format on task creation. Expected and confirmed: HTTP 422, with no silent coercion or acceptance of the malformed value.

**Test 2 — Status toggled repeatedly (regression check on a fixed bug).** A bug was found where moving a task from Done back to InProgress left the "Completed" indicator visible. After the fix, the task was toggled Done → InProgress → Done → InProgress multiple times in sequence. Expected and confirmed: the indicator correctly cleared and reappeared on every transition, not just the first, ruling out stale state reappearing after repeated use.

## Feature 2: Search + Combined Filters

### Backend test results

Command run: `python -m pytest tests\test_tasks.py`. Result: 40 passed. Command run: `python -m pytest` (full suite). Result: 41 passed.

This confirmed: `q` performs case-insensitive substring matching across title and description; `status` and `priority` return only matching tasks, with invalid enum values correctly returning HTTP 422; `assignee` performs case-insensitive exact matching, with unrecognized values returning an empty list (HTTP 200) rather than HTTP 422, since assignee has no fixed enum; empty or missing `assignee` applies no filter; all filters (`q`, `status`, `priority`, `assignee`) combine using AND logic; no-match cases, individually and combined, correctly return HTTP 200 with an empty list; and `GET /tasks` with no query parameters returns the full task list, unchanged from pre-Feature-2 behavior, confirmed via an explicit regression test.

### Manual browser checks

Searched a term known to exist in a task's title and confirmed matching task(s) appeared with non-matches excluded. Searched a term known to exist only in a task's description and confirmed it was found, validating that search covers both fields. Searched a term matching nothing and confirmed empty columns displayed with existing empty states rather than an error. Combined status, priority, and assignee filters together and confirmed AND logic correctly narrowed results. Selected an assignee with no matching tasks and confirmed empty columns with no error. Clicked "Clear filters" and confirmed all inputs reset to default with the full task list reappearing across all columns. Confirmed the assignee dropdown remained fully populated even while other filters were active, rather than shrinking to only currently-visible assignees.

### Behavior contract — before / after

Before: `GET /tasks` supported `status`, `priority`, and (after Feature 1) `overdue` as optional query parameters, with no parameters returning the full task list. After: `GET /tasks` additionally supports `q` and `assignee`, combinable with all existing parameters via AND logic, while calling it with no parameters still returns the identical full task list, confirmed via an explicit regression test. Status/priority validation behavior is unchanged.

### Break Test evidence

**Test 1 — Invalid filter value rejected even when combined with valid filters.** Sent a request combining a valid `status` with an invalid `priority` value. Expected and confirmed: HTTP 422 returned, not HTTP 200 with partial or empty results, verifying that validation runs before matching logic per the specified order of operations.

**Test 2 — Stale backend process isolated via direct API testing.** After the frontend filter bar was built, search appeared non-functional in the browser. Rather than assuming the frontend was at fault, the backend was tested directly with `GET /tasks?q=work` and `GET /tasks?q=nomatch-for-search` against the live running server. Both incorrectly returned all tasks regardless of the search term. Checking `/openapi.json` confirmed `q` and `assignee` were absent from the live schema despite being present in `app/main.py`, isolating the fault to a stale running process rather than the source code and preventing an incorrect frontend-side fix.

## Summary

Feature 1: baseline was the existing suite passing; after implementation, 22 tests passed; all acceptance criteria were walked manually in-browser; two break tests were performed (invalid date format, repeated status toggle). Feature 2: baseline was the 22 passing tests from Feature 1; after implementation, 41 tests passed across the full suite, including an explicit no-params regression check; all acceptance criteria were walked manually in-browser; two break tests were performed (invalid combined filter, stale-backend isolation).