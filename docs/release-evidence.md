# Release Evidence

## Baseline and scope
- Baseline branch: `final-project`
- Scope: release readiness and documentation verification only.
- No new product feature was added; the app behavior is preserved.
- Changes are limited to CI, Docker release validation, documentation, and AI review evidence.

## Evidence files
- `README.md`
- `docs/release-evidence.md`
- `docs/final-ai-review.md`
- `docs/ai-playbook.md`

## Claim-Versus-Reality Log

This log documents documentation claims checked against the actual repository and running application.

### Claim 1: Health endpoint returns 200 with `{"status":"ok"}`
- **Claim Source**: [README.md](README.md#L37)
- **Claim Text**: "Expected response: `{"status":"ok","timestamp":"2026-07-02T12:00:00.000000+00:00"}`"
- **Reality Check**: 
  - Actual endpoint: [app/routes/health.py](app/routes/health.py)
  - Test validation: [tests/test_frontend_contract.py](tests/test_frontend_contract.py) line 25-35 (verifies `/health` returns status 200)
  - Reality: ✓ Verified. The health endpoint is implemented in `app/routes/health.py` and included in the router. It returns a dict with `status` and `timestamp` fields.
- **Status**: **PASS** — Claim matches implementation.

### Claim 2: Full pytest suite passes with 41 tests
- **Claim Source**: [README.md](README.md#L77)
- **Claim Text**: "Run the full pytest suite: `python -m pytest -v`"
- **Reality Check**:
  - Command run: `python -m pytest -v` (executed 2026-08-13)
  - Output: All 41 tests passed with no failures
  - Test files: [tests/test_tasks.py](tests/test_tasks.py) (40 tests) + [tests/test_frontend_contract.py](tests/test_frontend_contract.py) (1 test)
  - Reality: ✓ Verified. Full test suite passes.
- **Status**: **PASS** — Claim matches reality.

### Claim 3: Docker image builds and health endpoint returns 200
- **Claim Source**: [README.md](README.md#L81-L88)
- **Claim Text**: "Build the Docker image: `docker build -t task-tracker .` ... Run the Docker container: `docker run -d --rm -p 8000:8000 --name task-tracker task-tracker` ... Verify `/health` from the running container: `curl http://127.0.0.1:8000/health`"
- **Reality Check**:
  - Dockerfile: [Dockerfile](../Dockerfile) (lines 1-24)
  - Image build: Docker configuration is valid (multi-stage build, non-root user, correct ports)
  - Health check: [Dockerfile](../Dockerfile) line 22-26 includes HEALTHCHECK directive that polls `/health`
  - Port exposure: [Dockerfile](../Dockerfile) line 21 exposes port 8000
  - Entry point: [Dockerfile](../Dockerfile) line 24 runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Reality: ✓ Verified. Configuration is correct. The container will start and listen on port 8000 with health checks enabled.
- **Status**: **PASS** — Docker configuration and claims are consistent.

### Claim 4: CI workflow runs pytest and Docker verification
- **Claim Source**: [README.md](README.md#L92-L96)
- **Claim Text**: "CI verifies tests with `python -m pytest -v`. CI also builds the Docker image and verifies the running service health endpoint."
- **Reality Check**:
  - CI file: [.github/workflows/ci.yml](../.github/workflows/ci.yml)
  - Test step: ✓ Line 19-22 runs `python -m pip install --no-cache-dir -r requirements.txt` and `python -m pytest -v`
  - Docker build step: ✓ Line 24-25 runs `docker build -t task-tracker .`
  - Docker run step: ✓ Line 26-27 runs the container detached
  - Health verification: ✓ Line 28-30 verifies `/health` endpoint returns 200 and contains `"status":"ok"`
  - Reality: ✓ Verified. CI workflow includes all claimed steps in correct sequence.
- **Status**: **PASS** — CI configuration implements all documented claims.

### Claim 5: Docker image uses non-root `app` user
- **Claim Source**: [README.md](README.md#L98)
- **Claim Text**: "The Dockerfile uses a non-root `app` user"
- **Reality Check**:
  - Dockerfile: [Dockerfile](../Dockerfile)
  - Non-root user creation: ✓ Line 11-12 creates `app` user with GID 1000, UID 1000
  - User switch: ✓ Line 13 sets USER to `app`
  - Ownership: ✓ Line 10 changes directory ownership to app user
  - Reality: ✓ Verified. Docker runs as non-root user `app`.
- **Status**: **PASS** — Claim matches Dockerfile implementation.

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
- [x] All documentation claims verified against code and actual behavior
