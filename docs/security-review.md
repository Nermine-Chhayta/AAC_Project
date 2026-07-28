# Security Review Finding Classification

This document classifies the AI-generated security findings for Module 5 grading.
The proposed grades are advisory: the final grading decision belongs to the student/instructor, especially where course scope affects whether a production risk is actionable.

## Summary

| Finding ID | Proposed grade | Risk |
|---|---|---|
| SEC-01 | Valid | Medium |
| SEC-02 | Valid | Medium |
| SEC-03 | Noise | Low |
| SEC-04 | Noise | Low |
| SEC-05 | Valid | Medium |
| SEC-06 | Valid | Low |
| SEC-07 | Noise | Low |
| SEC-08 | Valid | Low |
| SEC-09 | Noise | Low |

## Finding Details

### SEC-01

**Proposed grade:** Valid  
**Risk:** Medium

**Reason:** No auth may be intentional for Module 5, but a deployed/shared API would allow anyone with network access to read, create, update, and delete all tasks.

**Evidence used:** CRUD routes in `app/main.py` are declared without auth dependencies or middleware.

**Student decision to confirm:** Confirm whether "local/course demo only" is documented; if not, accept as a production-risk finding.

### SEC-02

**Proposed grade:** Valid  
**Risk:** Medium

**Reason:** Title has a cap, but other user-controlled strings and query filters appear unbounded, and list/search scans in-memory storage.

**Evidence used:** `description` and `assignee` have no max length in `app/models.py`; `_tasks` is an in-memory dict and `get_all_tasks` scans all values in `app/storage.py`.

**Student decision to confirm:** Confirm whether Module 5 expects only tiny local data. If yes, still valid as an outside-course risk.

### SEC-03

**Proposed grade:** Noise  
**Risk:** Low

**Reason:** The CORS point is mostly conditional. Origins are local-only, and the app has no cookie/session auth today, so credentials are not currently exposing protected data.

**Evidence used:** `app/main.py` allows local origins, all methods/headers, and credentials.

**Student decision to confirm:** Confirm whether grading accepts future production config risk. If strict repo-current impact is required, mark Noise.

### SEC-04

**Proposed grade:** Noise  
**Risk:** Low

**Reason:** Accepting arbitrary string IDs leads to normal 404 behavior, not clearly data exposure or injection. Echoing a missing ID in JSON is low-risk here.

**Evidence used:** `task_id: str` is used in routes; 404 detail includes the supplied ID; tests expect `"missing-task-id"` to return 404.

**Student decision to confirm:** Confirm whether API contract requires UUID-only IDs. Without that requirement, this is Noise.

### SEC-05

**Proposed grade:** Valid  
**Risk:** Medium

**Reason:** Tracking `.env` is a real credential hygiene issue, even if the current file appears non-secret. Future secret commits become more likely.

**Evidence used:** `.gitignore` ignores `.env`, but `git ls-files .env .env.example` showed `.env` is tracked; secret-keyword check returned 0 matches.

**Student decision to confirm:** Confirm whether `.env` contains only sample values. If yes, still valid, but severity may be Low/Medium.

### SEC-06

**Proposed grade:** Valid  
**Risk:** Low

**Reason:** Development defaults and reload behavior are fine locally, but risky if used as a production entrypoint.

**Evidence used:** `APP_ENV` defaults to `"development"` in `app/config.py`; direct run uses `reload=(APP_ENV == "development")`; README uses `--reload`.

**Student decision to confirm:** Confirm whether README is explicitly local-only. If yes, valid but low priority.

### SEC-07

**Proposed grade:** Noise  
**Risk:** Low

**Reason:** Including test/dev dependencies in the runtime image is generic hardening advice without a specific vulnerable package or exploit path shown.

**Evidence used:** `requirements.txt` includes `pytest`/`httpx`; Docker installs the full requirements file.

**Student decision to confirm:** Confirm whether production-hardening findings are in scope. If strict security-impact grading, mark Noise.

### SEC-08

**Proposed grade:** Valid  
**Risk:** Low

**Reason:** The container likely cannot serve `/` because the app serves `frontend/index.html`, but Docker does not copy `frontend/`. This is an availability/deployment risk.

**Evidence used:** Dockerfile copies `app` and `requirements.txt` only; `app/main.py` root route serves `frontend/index.html`.

**Student decision to confirm:** Confirm whether Docker deployment is part of grading. If yes, valid.

### SEC-09

**Proposed grade:** Noise  
**Risk:** Low

**Reason:** This is broad supply-chain advice, but unsupported as an actionable repo-specific security finding without a threat model or vulnerable dependency/action evidence.

**Evidence used:** Workflow uses `actions/checkout@v4` and `actions/setup-python@v4`; requirements are version-pinned but not hash-locked.

**Student decision to confirm:** Confirm whether the rubric rewards advanced CI hardening. For Module 5, likely Noise.

## Files Referenced

- `app/main.py`
- `app/models.py`
- `app/storage.py`
- `app/config.py`
- `Dockerfile`
- `requirements.txt`
- `.github/workflows/ci.yml`
- `.gitignore`
- `.env`
- `.env.example`
- `README.md`
- `tests/test_tasks.py`

## Notes

- No new findings are introduced here.
- Severity is not upgraded beyond the submitted findings.
- Authentication is treated as both an intentional course-scope omission and a real production risk.
