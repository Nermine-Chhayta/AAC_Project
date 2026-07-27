# Defines the /health endpoint used to verify the API is running.

from datetime import datetime, timezone
from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, status_code=200)
def get_health() -> HealthResponse:
    """Return a simple API health status payload.

    Returns:
        HealthResponse: A payload containing status and timestamp.

    Example:
        GET /health
    """
    # Returns a simple status payload with the current UTC timestamp in ISO format
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )