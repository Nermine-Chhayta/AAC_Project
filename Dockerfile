FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

RUN adduser --disabled-password --gecos "" app
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app ./app
COPY frontend ./frontend
COPY requirements.txt .

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD python -c "import urllib.request, sys; r = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3); sys.exit(0 if r.status == 200 else 1)"
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
