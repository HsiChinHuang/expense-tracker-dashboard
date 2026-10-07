"""Pydantic 2 response schema for the health check endpoint.

Mirrors the HealthResponse contract from Chapter 7 §7.2.1 of the
product requirements (REQ-TECH-022).
"""

from typing import Literal

from pydantic import BaseModel

DatabaseBackend = Literal["postgresql", "sqlite"]
HealthStatus = Literal["ok", "degraded"]


class HealthResponse(BaseModel):
    """Response body for ``GET /api/v1/health``.

    Attributes:
        status: Overall service health; ``"ok"`` when healthy and no
            fallback is active, ``"degraded"`` otherwise.
        database: Configured database backend name.
        fallback_active: Whether the SQLite fallback is currently active.
        version: Application version string served by the API.
    """

    status: HealthStatus
    database: DatabaseBackend
    fallback_active: bool
    version: str
