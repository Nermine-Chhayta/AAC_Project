# AGENTS.md

## Project summary

This repository is a FastAPI-based Task Tracker final project with a static frontend served from `frontend/index.html`.
The backend is implemented in `app/main.py` and uses FastAPI, Pydantic models, and in-memory task storage from `app/storage.py`.

## Tech stack

- Python 3.11-compatible runtime
- FastAPI web framework
- Uvicorn ASGI server
- Pydantic v2 for request and response models
- python-dotenv for optional `.env` configuration in `app/config.py`
- Pytest for automated tests

## Verified commands

Install dependencies:
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -r requirements.txt
```

Run locally:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run tests:
```bash
python -m pytest -v
```

Build Docker image:
```bash
docker build -t task-tracker .
```

Run container:
```bash
docker run --rm -p 8000:8000 task-tracker
```

Health check:
```bash
curl http://127.0.0.1:8000/health
```

## Project rules

- Do not make unexpected edits to backend or frontend application logic unless a test failure proves a change is required.
- Prefer documentation and test evidence over code changes.
- Preserve existing behavior unless the user explicitly asks for a feature or bug fix.
- Keep CI and Docker validation simple, explicit, and failure-safe.

## Guardrails

- Read the repo docs, README, and tests before modifying code.
- Do not alter `app/` behavior unless the change is directly supported by test failures.
- Use the existing app entrypoint, health endpoint, and commands for verification.
- Avoid copying local `.env` files into Docker images.

## Notes

- `pytest.ini` configures `pythonpath = .` and `testpaths = tests`.
- The repository includes `.env.example` at the root.
- Dockerfile is configured to use a non-root `app` user.

## Security and AI review

- Security guardrails are in place to avoid unexpected app logic changes.
- No new product feature was added; updates are limited to verification and documentation.
- AI assistance was used for documentation, CI, and release evidence improvements only.
- See `docs/final-ai-review.md` for the final AI review, ownership statement, and graded findings.
