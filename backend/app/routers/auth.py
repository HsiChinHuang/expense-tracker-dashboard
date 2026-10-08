"""Auth endpoints: register / login / me (t8, REQ-API-020/021/022).

The router is mounted under ``/api/v1/auth`` and registered in
``create_app()`` *after* the health router (REQ-BE-141 registration-order
intent). Bodies/outputs are Pydantic-validated; all error responses flow
through the ``AppError`` handler so the shape is always
``{detail, code, field}`` (REQ-ARCH-024).

``Annotated[T, Depends(...)]`` is used instead of ``T = Depends(...)``
because ruff's B008 rule (selected project-wide) rejects the latter.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, session: Annotated[Session, Depends(get_db)]) -> User:
    """Register a new account (FR-AUTH-1, REQ-API-020).

    Args:
        body: Validated register payload.
        session: Request-scoped database session.

    Returns:
        User: The persisted user (rendered through ``UserResponse``,
        which exposes only the five public fields).

    Raises:
        AppError: 409 DUPLICATE_EMAIL / DUPLICATE_USERNAME.
    """
    return register_user(session, body.email, body.username, body.password)


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, session: Annotated[Session, Depends(get_db)]) -> LoginResponse:
    """Log in and receive a 24-hour access token (FR-AUTH-2, REQ-API-021).

    Args:
        body: Validated login payload.
        session: Request-scoped database session.

    Returns:
        LoginResponse: ``{access_token, token_type, user}``.

    Raises:
        AppError: 401 INVALID_CREDENTIALS / USER_INACTIVE.
    """
    result = login_user(session, body.email, body.password)
    return LoginResponse(
        access_token=result.access_token,
        token_type="bearer",
        user=UserResponse.model_validate(result.user),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Return the current user for a valid bearer token (FR-AUTH-3).

    Args:
        current_user: User resolved by ``get_current_user``.

    Returns:
        User: The authenticated user (public five fields only).
    """
    return current_user
