# Task Tracker API

A lightweight REST API for creating and tracking tasks, built with FastAPI and Pydantic. This project uses simple JSON file storage instead of a database, keeping the stack minimal and easy to run locally for learning purposes.

## Setup

### 1. Create a virtual environment and install dependencies

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and adjust values if needed:

**Linux / macOS**
```bash
cp .env.example .env
```

**Windows (PowerShell)**
```powershell
Copy-Item .env.example .env
```

### 3. Start the server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### 4. Test the health endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-07-02T12:00:00.000000+00:00"
}
```

## Final Project

- Branch: `final-project`
- Evidence files:
  - `README.md`
  - `docs/release-evidence.md`
  - `docs/final-ai-review.md`
  - `docs/ai-playbook.md`
- AI assistance summary:
  - AI was used to help plan documentation, confirm release-readiness steps, and draft evidence summaries.
  - All AI-generated content was manually reviewed, validated against the running app, and limited to verification and documentation work.
  - No product feature changes were introduced; the app behavior was preserved.

This submission is based on the `final-project` branch and preserves the existing Task Tracker app behavior.
No new product feature was added; verification and release readiness were the only changes.

### Verified commands

Start the backend API:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify the health endpoint:
```bash
curl http://127.0.0.1:8000/health
```

Run the full pytest suite:
```bash
python -m pytest -v
```

Build the Docker image:
```bash
docker build -t task-tracker .
```

Run the Docker container:
```bash
docker run -d --rm -p 8000:8000 --name task-tracker task-tracker
```

Verify `/health` from the running container:
```bash
curl http://127.0.0.1:8000/health
```

Stop the container:
```bash
docker stop task-tracker
```

### Release readiness

- CI verifies tests with `python -m pytest -v`.
- CI also builds the Docker image and verifies the running service health endpoint.
- The Dockerfile uses a non-root `app` user and avoids copying local `.env` files into the image.
- `.dockerignore` excludes environment files, Git metadata, virtual environments, and common temporary artifacts.

### Notes

- CI uses Python 3.11.
- The app is served by `uvicorn` on port `8000`.
