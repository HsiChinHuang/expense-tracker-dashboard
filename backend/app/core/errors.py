"""Application error type and FastAPI handlers (REQ-BE-110/111, REQ-ARCH-024).

Every error the API returns renders the same three-key shape
``{"detail": ..., "code": ..., "field": ...}`` (Chapter 7 §7.8). The codes
are the Appendix B names verbatim (REQ-BE-112); this module defines only
the subset t8's auth vertical needs — the remaining Appendix B codes land
with the phase_3 CRUD issues that surface them.

Handlers are registered through :func:`register_error_handlers` so
``create_app()`` stays readable and the wiring is testable in one place.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("app.core.errors")

__all__ = [
    "AppError",
    "DATABASE_UNAVAILABLE",
    "DUPLICATE_EMAIL",
    "DUPLICATE_USERNAME",
    "INVALID_CREDENTIALS",
    "TOKEN_EXPIRED",
    "TOKEN_INVALID",
    "UNAUTHORIZED",
    "USER_INACTIVE",
    "VALIDATION_ERROR",
    "register_error_handlers",
]

VALIDATION_ERROR = "VALIDATION_ERROR"
DUPLICATE_EMAIL = "DUPLICATE_EMAIL"
DUPLICATE_USERNAME = "DUPLICATE_USERNAME"
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
UNAUTHORIZED = "UNAUTHORIZED"
TOKEN_INVALID = "TOKEN_INVALID"
TOKEN_EXPIRED = "TOKEN_EXPIRED"
USER_INACTIVE = "USER_INACTIVE"
DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"


class AppError(Exception):
    """Domain error that maps directly onto the API error shape.

    Attributes:
        status_code: HTTP status the handler will return.
        code: Appendix B error code (verbatim).
        detail: Human-readable message.
        field: Offending request member where the contract names one, else
            ``None`` (the key is still present in the rendered body).
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        detail: str,
        field: str | None = None,
    ) -> None:
        """Record the HTTP status/code/field triple for the error response.

        Args:
            status_code: HTTP status code to return.
            code: Appendix B error code.
            detail: Human-readable message.
            field: Offending member name, or ``None``.
        """
        super().__init__(detail)
        self.status_code = status_code
        self.code = code
        self.detail = detail
        self.field = field

    def to_response(self) -> JSONResponse:
        """Render this error as the contract JSON response.

        Returns:
            JSONResponse: Body with exactly the keys ``detail``, ``code``
            and ``field``.
        """
        return JSONResponse(
            status_code=self.status_code,
            content={"detail": self.detail, "code": self.code, "field": self.field},
        )


def _first_error_field(exc: RequestValidationError) -> tuple[str | None, str]:
    """Extract the offending member name from a validation error.

    FastAPI reports locations as tuples such as ``("body", "email")``; the
    last non-locator segment names the request member.

    Args:
        exc: The raised validation error.

    Returns:
        tuple[str | None, str]: The field name (or ``None``) and a short
        rendered message.
    """
    errors = exc.errors()
    first: dict[str, Any] = errors[0] if errors else {}
    raw_loc = first.get("loc", ())
    segments = [str(part) for part in raw_loc if part not in ("body", "query", "path")]
    field = segments[-1] if segments else None
    detail = str(first.get("msg", "Invalid request"))
    return field, detail


def register_error_handlers(application: FastAPI) -> None:
    """Attach the ``{detail, code, field}`` handlers to an application.

    Args:
        application: The FastAPI application to wire.
    """

    @application.exception_handler(AppError)
    async def _handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        """Return the contract shape for a domain error."""
        return exc.to_response()

    @application.exception_handler(RequestValidationError)
    async def _handle_validation_error(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Map request-body validation failures to 422 VALIDATION_ERROR."""
        field, detail = _first_error_field(exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": detail, "code": VALIDATION_ERROR, "field": field},
        )

    @application.exception_handler(SQLAlchemyError)
    async def _handle_database_error(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Map unexpected database failures to 503 DATABASE_UNAVAILABLE.

        The original SQLAlchemy message is deliberately not echoed to the
        client and is summarized (error type only) in the log line.
        """
        logger.error(
            "auth.database_unavailable",
            extra={"extra_fields": {"error_type": type(exc).__name__}},
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database is currently unavailable",
                "code": DATABASE_UNAVAILABLE,
                "field": None,
            },
        )
