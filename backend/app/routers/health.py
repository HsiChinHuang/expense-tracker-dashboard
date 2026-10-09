"""Public health check endpoint (FR-HEALTH-1, Chapter 7 §7.2.1).

The endpoint is public, returns the four documented fields through a
Pydantic 2 response model, and reports the LIVE database state (t25,
REQ-BE-132, REQ-OPS-011/012): ``database`` is derived from the bound
engine's dialect (or the configured URL when no engine is bound),
``fallback_active`` from ``is_fallback()``, and ``status`` is
``"degraded"`` exactly when a fallback is active.
"""

from fastapi import APIRouter, Request
from sqlalchemy.engine import make_url

from app.config import get_settings
from app.database import is_fallback
from app.schemas.health import DatabaseBackend, HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Report service health without requiring authentication.

    Args:
        request: Incoming request, used to read the bound engine (when
            the startup handler registered one) and the version.

    Returns:
        HealthResponse: Live health payload where ``status == "ok"``
        iff ``fallback_active`` is False (REQ-OPS-011/012).
    """
    engine = getattr(request.app.state, "db_engine", None)
    if engine is not None:
        backend: DatabaseBackend = (
            "sqlite" if engine.url.get_backend_name() == "sqlite" else "postgresql"
        )
    else:
        backend = (
            "sqlite"
            if make_url(get_settings().DATABASE_URL).get_backend_name() == "sqlite"
            else "postgresql"
        )
    fallback_active = is_fallback()
    return HealthResponse(
        status="degraded" if fallback_active else "ok",
        database=backend,
        fallback_active=fallback_active,
        version=request.app.version,
    )
