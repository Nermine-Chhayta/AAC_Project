# Release Evidence

## Baseline and scope
- Baseline branch: `final-project`
- Scope: release readiness and documentation verification only.
- No new product feature was added; the app behavior is preserved.
- Changes are limited to CI, Docker release validation, documentation, and AI review evidence.

## Verified commands

- Start backend API:
  ```bash
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

- Health check:
  ```bash
  curl http://127.0.0.1:8000/health
  ```
  Verified response:
  ```json
  {"status":"ok","timestamp":"2026-07-29T15:25:57.305278+00:00"}
  ```

- Full pytest suite:
  ```bash
  python -m pytest -v
  ```
  Result: `41 passed`

- Docker build:
  ```bash
  docker build -t task-tracker .
  ```

- Docker run:
  ```bash
  docker run -d --rm -p 8000:8000 --name task-tracker task-tracker
  ```

- Container health endpoint verification:
  ```bash
  curl http://127.0.0.1:8000/health
  ```
  Verified response contains: `"status":"ok"`

- Stop container:
  ```bash
  docker stop task-tracker
  ```

## CI

- Workflow file: `.github/workflows/ci.yml`
- Runs on `ubuntu-latest`.
- Python version: `3.11`
- Dependency installation: `python -m pip install --no-cache-dir -r requirements.txt`
- Test command: `python -m pytest -v`
- Docker verification:
  - `docker build -t task-tracker .`
  - run the image detached
  - verify `/health` returns `200` and `{"status":"ok"}`

## Docker

- Dockerfile uses a non-root `app` user.
- `.dockerignore` excludes `.env`, `*.env`, `.git`, `venv`, `.venv`, and other build artifacts.
- The container exposes port `8000` and runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Healthcheck is configured to poll `/health` from inside the container.

## Manual verification

- [x] Local `pytest` run completed.
- [x] Local Docker build and run completed.
- [x] Manual `/health` endpoint check completed.
- [x] No new product feature was added.

## Release readiness checklist

- [x] Pytest passes (`41 passed`)
- [x] Docker image builds successfully
- [x] Docker container starts successfully
- [x] `/health` endpoint verified inside container
- [x] CI workflow includes test and Docker verification
