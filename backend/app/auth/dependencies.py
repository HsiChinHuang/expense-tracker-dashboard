# mypy: disable-error-code="import-untyped"
"""FastAPI authentication dependency (t8, REQ-BE-041, REQ-ARCH-041).

``get_current_user`` extracts the ``Authorization: Bearer <token>``
header, delegates every JWT validation step to t7's
:func:`~app.auth.jwt.decode_access_token` (no re-implementation of JWT
logic here), then loads the user and enforces ``is_active``. The four
401 codes are distinct per REQ-SEC-022:

- ``UNAUTHORIZED``   — no/ malformed Authorization header
- ``TOKEN_INVALID``  — signature/claims failed validation (t7 TokenError)
- ``TOKEN_EXPIRED``  — the TokenError was caused by jose's
  ExpiredSignatureError (t7's TokenError carries no reason code, so the
  ``__cause__`` chain is inspected; validation is never re-run)
- ``USER_INACTIVE``  — valid token, disabled account

``HTTPBearer(auto_error=False)`` is required so a missing header reaches
this mapping instead of FastAPI's built-in 403 shape.
"""

import logging
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError
from sqlalchemy.orm import Session

from app.auth.jwt import TokenError, decode_access_token
from app.core.errors import TOKEN_EXPIRED, TOKEN_INVALID, UNAUTHORIZED, AppError
from app.database import get_db
from app.models.user import User
from app.services.auth_service import get_user_by_token_claims

logger = logging.getLogger("app.auth.dependencies")
"""Module logger; records carry no tokens, emails, or secrets."""

_bearer_scheme = HTTPBearer(auto_error=False)
"""Bearer scheme with auto_error disabled (see module docstring)."""


def _client_ip(request: Request) -> str | None:
    """Return the best-effort client IP for log context (REQ-BE-042).

    Args:
        request: The incoming request.

    Returns:
        str | None: The direct client host, or ``None`` when unknown.
    """
    return request.client.host if request.client else None


def get_client_ip(request: Request) -> str | None:
    """Return the client IP for audit capture (REQ-BE-042).

    Chapter 6 6.5.4's frozen single rule, no alternatives: a truthy
    ``X-Forwarded-For`` header yields its first hop, whitespace-
    stripped; an absent OR empty header falls back to the direct
    ``request.client.host`` (``None`` when the transport reports no
    client). No truncation logic is invented (review_plan: the survey's
    "<= 45 chars" clause is dropped as unspecified behavior).

    Args:
        request: The incoming request.

    Returns:
        str | None: The best-effort client IP, or ``None`` when unknown.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the current user from the request's bearer token.

    Args:
        request: Incoming request (used for sanitized log context).
        credentials: Parsed bearer credentials, or ``None`` when the
            header is absent/malformed.
        session: Database session from ``get_db``.

    Returns:
        User: The active user the token addresses.

    Raises:
        AppError: 401 with UNAUTHORIZED, TOKEN_INVALID, TOKEN_EXPIRED,
            or USER_INACTIVE (all distinct per REQ-SEC-022).
    """
    if credentials is None or not credentials.credentials:
        logger.warning(
            "auth.unauthorized",
            extra={
                "extra_fields": {
                    "reason": "missing_header",
                    "client_ip": _client_ip(request),
                }
            },
        )
        raise AppError(401, UNAUTHORIZED, "Not authenticated")

    try:
        claims = decode_access_token(credentials.credentials)
    except TokenError as exc:
        if isinstance(exc.__cause__, ExpiredSignatureError):
            logger.warning(
                "auth.token_expired",
                extra={"extra_fields": {"client_ip": _client_ip(request)}},
            )
            raise AppError(401, TOKEN_EXPIRED, "Token has expired") from None
        logger.warning(
            "auth.token_invalid",
            extra={"extra_fields": {"client_ip": _client_ip(request)}},
        )
        raise AppError(401, TOKEN_INVALID, "Invalid access token") from None

    return get_user_by_token_claims(session, claims)
