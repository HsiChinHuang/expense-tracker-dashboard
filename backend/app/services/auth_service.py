"""Auth service: registration and login orchestration (t8, REQ-BE-050/051).

The service composes t7's primitives (``hash_password`` / ``verify_password``
/ ``verify_dummy`` / ``create_access_token``) and never re-implements crypto.

t7 carry-forward #1 (decision recorded here per the t8 groom): the locked
passlib 1.7.4 / bcrypt 4.0.1 pair raises plain ``ValueError`` — not
``UnknownHashError`` — for malformed stored hashes such as ``$2b$12$``,
``$2b$12$short`` or ``$2y$05$`` + 22 chars. t7's ``verify_password`` catches
``UnknownHashError`` only and its catch is pinned by t7's own AC, so the fix
is taken HERE instead: :meth:`authenticate_user` wraps the verify call in
``except ValueError`` and treats a corrupt stored hash as a credential
failure (then pays the dummy-verify cost, like any other failure). t7 is
merged and its module is deliberately left untouched.

Logging hygiene (REQ-BE-121/122, ac5): log records carry only the sha256
email identifier (first 16 hex chars of the normalized email's digest) —
never a raw email, password, token, or bcrypt hash.
"""

import hashlib
import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_dummy, verify_password
from app.core.errors import (
    DUPLICATE_EMAIL,
    DUPLICATE_USERNAME,
    INVALID_CREDENTIALS,
    TOKEN_INVALID,
    USER_INACTIVE,
    AppError,
)
from app.models.user import User

logger = logging.getLogger("app.services.auth_service")
"""Module logger; ac5 asserts observable record content on this logger."""

EMAIL_HASH_IDENTIFIER_LENGTH = 16
"""Length of the truncated sha256 email identifier used in logs."""

INVALID_CREDENTIALS_DETAIL = "Invalid email or password"
"""Single shared 401 detail: wrong password and unknown email are
byte-identical bodies (REQ-SEC-022, no user enumeration)."""


def email_identifier(email: str) -> str:
    """Return the non-reversible log identifier for an email.

    Args:
        email: Normalized (lowercased) email address.

    Returns:
        str: First 16 hex characters of the email's sha256 digest.
    """
    return hashlib.sha256(email.encode("utf-8")).hexdigest()[:EMAIL_HASH_IDENTIFIER_LENGTH]


@dataclass(frozen=True)
class AuthenticatedUser:
    """Result of a successful login: the user row and its fresh token.

    Attributes:
        user: The authenticated ``User`` row.
        access_token: A signed 24-hour JWT whose ``sub`` is the user id.
    """

    user: User
    access_token: str


def _normalize_email(email: str) -> str:
    """Lowercase an email before any uniqueness check or storage.

    Args:
        email: Raw candidate email.

    Returns:
        str: The lowercased email (REQ-BE-050).
    """
    return email.lower()


def _get_user_by_email(session: Session, email: str) -> User | None:
    """Load the user whose stored email equals the normalized email.

    Args:
        session: Active database session.
        email: Already-normalized email.

    Returns:
        User | None: The matching row, or ``None``.
    """
    return session.execute(select(User).where(User.email == email)).scalar_one_or_none()


def _get_user_by_username(session: Session, username: str) -> User | None:
    """Load the user whose stored username equals ``username`` exactly.

    Username uniqueness stays case-sensitive per t6's merged DB behavior.

    Args:
        session: Active database session.
        username: Candidate username, case preserved.

    Returns:
        User | None: The matching row, or ``None``.
    """
    return session.execute(select(User).where(User.username == username)).scalar_one_or_none()


def _log_failure(reason: str, email: str, username: str | None) -> None:
    """Emit a sanitized auth-failure record (no raw email/password).

    Args:
        reason: Machine-readable failure reason.
        email: Normalized email (only its digest identifier is logged).
        username: Candidate username, or ``None`` when unknown.
    """
    logger.warning(
        reason,
        extra={"extra_fields": {"email_id": email_identifier(email), "username": username}},
    )


def register_user(session: Session, email: str, username: str, password: str) -> User:
    """Register a new user account (REQ-BE-050, REQ-API-020).

    The email is lowercased *before* the duplicate checks and storage;
    usernames keep their exact case and are matched exactly.

    Args:
        session: Active database session.
        email: Candidate email.
        username: Candidate username.
        password: Plaintext password (hashed, never stored or logged).

    Returns:
        User: The persisted row.

    Raises:
        AppError: 409 DUPLICATE_EMAIL or DUPLICATE_USERNAME.
    """
    normalized_email = _normalize_email(email)
    if _get_user_by_email(session, normalized_email) is not None:
        _log_failure("auth.register_duplicate", normalized_email, username)
        raise AppError(409, DUPLICATE_EMAIL, "Email already registered", field="email")
    if _get_user_by_username(session, username) is not None:
        _log_failure("auth.register_duplicate", normalized_email, username)
        raise AppError(409, DUPLICATE_USERNAME, "Username already taken", field="username")

    user = User(
        email=normalized_email,
        username=username,
        hashed_password=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info(
        "auth.register",
        extra={"extra_fields": {"email_id": email_identifier(normalized_email)}},
    )
    return user


def authenticate_user(session: Session, email: str, password: str) -> User:
    """Verify credentials and return the active user row (REQ-BE-051).

    Failure paths (unknown email, wrong password, corrupt stored hash,
    inactive account) all raise :class:`AppError` 401. The unknown-email
    path pays one ``verify_dummy`` cycle so it costs the same as a
    wrong-password attempt (REQ-SEC-023); the corrupt-hash path pays it
    too so that failure keeps the same cost profile. The wrong-password
    path never calls the decoy — it already ran a real cost-12 verify,
    and this asymmetry is pinned by a spy test. The corrupt-hash path is
    the t7 carry-forward #1 service-layer ``ValueError`` catch documented
    in the module docstring.

    Args:
        session: Active database session.
        email: Candidate email.
        password: Candidate plaintext password.

    Returns:
        User: The authenticated, active user row.

    Raises:
        AppError: 401 INVALID_CREDENTIALS for any credential failure, or
            401 USER_INACTIVE for a disabled account.
    """
    normalized_email = _normalize_email(email)
    user = _get_user_by_email(session, normalized_email)

    if user is None:
        verify_dummy(password)
        _log_failure("auth.login_invalid_credentials", normalized_email, None)
        raise AppError(401, INVALID_CREDENTIALS, INVALID_CREDENTIALS_DETAIL)

    try:
        password_ok = verify_password(password, user.hashed_password)
    except ValueError:
        # t7 carry-forward #1: passlib raises plain ValueError (not
        # UnknownHashError) for malformed stored hashes. Treat as a
        # credential failure and pay the dummy cost, per the module
        # docstring decision.
        verify_dummy(password)
        _log_failure("auth.login_invalid_credentials", normalized_email, user.username)
        raise AppError(401, INVALID_CREDENTIALS, INVALID_CREDENTIALS_DETAIL) from None

    if not password_ok:
        _log_failure("auth.login_invalid_credentials", normalized_email, user.username)
        raise AppError(401, INVALID_CREDENTIALS, INVALID_CREDENTIALS_DETAIL)

    if not user.is_active:
        _log_failure("auth.login_inactive", normalized_email, user.username)
        raise AppError(401, USER_INACTIVE, "User account is inactive")

    return user


def login_user(session: Session, email: str, password: str) -> AuthenticatedUser:
    """Authenticate and issue an access token (REQ-BE-051, REQ-API-021).

    Args:
        session: Active database session.
        email: Candidate email.
        password: Candidate plaintext password.

    Returns:
        AuthenticatedUser: The user row plus a JWT whose ``sub`` is the
        user id string.

    Raises:
        AppError: Whatever :func:`authenticate_user` raises.
    """
    user = authenticate_user(session, email, password)
    token = create_access_token(subject=str(user.id))
    logger.info(
        "auth.login",
        extra={"extra_fields": {"email_id": email_identifier(_normalize_email(email))}},
    )
    return AuthenticatedUser(user=user, access_token=token)


def get_user_by_token_claims(session: Session, claims: dict[str, object]) -> User:
    """Load the active user addressed by decoded token claims.

    Args:
        session: Active database session.
        claims: Claims returned by ``decode_access_token``.

    Returns:
        User: The active user row.

    Raises:
        AppError: 401 TOKEN_INVALID when ``sub`` is missing or not a
            UUID, or 401 USER_INACTIVE when the account is disabled.
    """
    subject = claims.get("sub")
    try:
        user_id = UUID(str(subject))
    except ValueError:
        logger.warning("auth.token_invalid", extra={"extra_fields": {"reason": "bad_sub"}})
        raise AppError(401, TOKEN_INVALID, "Invalid access token") from None

    user = session.get(User, user_id)
    if user is None:
        logger.warning("auth.token_invalid", extra={"extra_fields": {"reason": "no_such_user"}})
        raise AppError(401, TOKEN_INVALID, "Invalid access token")
    if not user.is_active:
        _log_failure("auth.login_inactive", user.email, user.username)
        raise AppError(401, USER_INACTIVE, "User account is inactive")
    return user


__all__ = [
    "AuthenticatedUser",
    "authenticate_user",
    "email_identifier",
    "get_user_by_token_claims",
    "login_user",
    "register_user",
]
