"""Pydantic request/response schemas for the auth endpoints (t8).

Request bodies are Pydantic-validated (REQ-SEC-040/041): email shape,
username 3-50 characters without whitespace, and password 8-72 characters
with the bcrypt ceiling enforced on the UTF-8 *byte* length (REQ-BE-031).

``pydantic.EmailStr`` is deliberately not used: ``email-validator`` is not
in the lockfile and t8 adds no dependencies, so the email shape is checked
with a ``field_validator`` and a conservative pattern instead.

The public user representation is exactly the five documented fields —
``hashed_password`` (or any password-ish casing) never leaves the API.
"""

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
"""Conservative single-at email shape (email-validator is unavailable)."""

USERNAME_PATTERN = re.compile(r"^\S{3,50}$")
"""Username: 3-50 characters, no whitespace anywhere (REQ-PROJ-008)."""

PASSWORD_MIN_CHARS = 8
"""Minimum password length in characters (REQ-BE-031)."""

PASSWORD_MAX_CHARS = 72
"""Maximum password length in characters (REQ-BE-031)."""

PASSWORD_MAX_BYTES = 72
"""bcrypt input ceiling, enforced on UTF-8 bytes (REQ-BE-031)."""


class RegisterRequest(BaseModel):
    """Request body for ``POST /api/v1/auth/register`` (REQ-API-020).

    Attributes:
        email: Candidate email; normalized to lowercase by the service.
        username: Candidate username (uniqueness is case-sensitive).
        password: Plaintext password; validated then bcrypt-hashed.
    """

    email: str = Field(min_length=3, max_length=255)
    username: str
    password: str

    @field_validator("email")
    @classmethod
    def _valid_email_shape(cls, value: str) -> str:
        """Reject strings that are not a basic email shape.

        Args:
            value: Candidate email.

        Returns:
            str: The email unchanged.

        Raises:
            ValueError: When the shape does not match EMAIL_PATTERN.
        """
        if not EMAIL_PATTERN.match(value):
            raise ValueError("value is not a valid email address")
        return value

    @field_validator("username")
    @classmethod
    def _valid_username(cls, value: str) -> str:
        """Enforce the 3-50 non-whitespace username rule.

        Args:
            value: Candidate username.

        Returns:
            str: The username unchanged.

        Raises:
            ValueError: When the username is malformed.
        """
        if not USERNAME_PATTERN.fullmatch(value):
            raise ValueError("username must be 3-50 characters with no whitespace")
        return value

    @field_validator("password")
    @classmethod
    def _valid_password(cls, value: str) -> str:
        """Enforce 8-72 characters and at most 72 UTF-8 bytes.

        Args:
            value: Candidate password.

        Returns:
            str: The password unchanged.

        Raises:
            ValueError: When the password violates the length rules.
        """
        if len(value) < PASSWORD_MIN_CHARS or len(value) > PASSWORD_MAX_CHARS:
            raise ValueError("password must be between 8 and 72 characters")
        if len(value.encode("utf-8")) > PASSWORD_MAX_BYTES:
            raise ValueError("password must be at most 72 UTF-8 bytes")
        return value


class LoginRequest(BaseModel):
    """Request body for ``POST /api/v1/auth/login`` (REQ-API-021).

    Attributes:
        email: Account email (matched case-insensitively by the service).
        password: Candidate plaintext password.
    """

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def _valid_email_shape(cls, value: str) -> str:
        """Reject strings that are not a basic email shape.

        Args:
            value: Candidate email.

        Returns:
            str: The email unchanged.

        Raises:
            ValueError: When the shape does not match EMAIL_PATTERN.
        """
        if not EMAIL_PATTERN.match(value):
            raise ValueError("value is not a valid email address")
        return value


class UserResponse(BaseModel):
    """Public user representation — exactly five fields (REQ-API-020).

    ``from_attributes`` lets routes build it from the ORM ``User`` row
    while the model itself never carries a password field of any casing.

    Attributes:
        id: User UUID (serialized as its canonical string form).
        email: Lowercased stored email.
        username: Stored username.
        is_active: Account activation flag.
        created_at: Creation timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime


class LoginResponse(BaseModel):
    """Response body for ``POST /api/v1/auth/login`` (REQ-API-021).

    Attributes:
        access_token: Signed 24-hour JWT.
        token_type: Always ``"bearer"``.
        user: The authenticated user's public representation.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
