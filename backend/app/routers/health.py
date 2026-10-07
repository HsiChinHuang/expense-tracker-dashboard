"""Public health check endpoint (FR-HEALTH-1, Chapter 7 §7.2.1).

Phase 1 ships the contract skeleton: the endpoint is public, returns the
four documented fields through a Pydantic 2 response model, and reports
honest static values. Live database probing and SQLite fallback
reporting are phase_5 scope (REQ-PROD-017).
"""

from typing import Final

from fastapi import APIRouter, Request

from app.schemas.health import DatabaseBackend, HealthResponse

DATABASE_BACKEND: Final[DatabaseBackend] = "postgresql"
"""Configured database backend for this deployment (phase-1 constant)."""

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Report service health without requiring authentication.

    Args:
        request: Incoming request, used to read the application version.

    Returns:
        HealthResponse: Static phase-1 health payload where
        ``status == "ok"`` iff ``fallback_active`` is False.
    """
    fallback_active = False
    return HealthResponse(
        status="ok" if not fallback_active else "degraded",
        database=DATABASE_BACKEND,
        fallback_active=fallback_active,
        version=request.app.version,
    )
