# Pydantic model defining the response schema for the /health endpoint.

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: str
