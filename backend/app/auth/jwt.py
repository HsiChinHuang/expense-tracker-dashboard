# mypy: disable-error-code="import-untyped"
"""HS256 JWT issue/decode primitives (t7, REQ-BE-020/021/022/023).

The algorithm list always comes from settings — never from the token
header — so ``alg=none`` forgeries are rejected (REQ-BE-022). Every
failure surfaces as the module-local :class:`TokenError` so t8 can map
it to HTTP 401 without this module importing FastAPI.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError
from jose import jwt as jose_jwt

from app.config import get_settings

__all__ = ["TokenError", "create_access_token", "decode_access_token"]


class TokenError(Exception):
    """Raised when a token fails any validation step (t8 maps it to 401).

    Extends ``Exception`` specifically and is caught specifically —
    callers must never need ``except Exception`` to handle auth failures.
    """


def create_access_token(subject: str) -> str:
    """Issue a signed 24-hour access token for a user id (REQ-BE-020/023).

    Args:
        subject: The user id string placed in the ``sub`` claim.

    Returns:
        str: An HS256 JWT carrying exactly the claims ``sub``, ``iss``,
            ``aud``, ``iat``, ``exp`` and ``type``, signed with
            ``settings.JWT_SECRET`` with ``exp - iat`` equal to
            ``JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60``.
    """
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    claims = {
        "sub": subject,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "access",
    }
    return cast(
        "str",
        jose_jwt.encode(
            claims,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        ),
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate and decode an access token (REQ-BE-021/022/SEC-021).

    Signature, expiry, audience, issuer and the ``type == "access"``
    claim are all validated; the algorithm set comes exclusively from
    ``settings.JWT_ALGORITHM`` so a hostile header cannot downgrade it.

    Args:
        token: The compact JWT string to validate.

    Returns:
        dict[str, Any]: The decoded claims when every check passes.

    Raises:
        TokenError: On any validation failure (invalid signature,
            expired token, wrong audience/issuer, wrong token type or
            a disallowed algorithm such as ``none``).
    """
    settings = get_settings()
    try:
        claims = jose_jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except JWTError as exc:
        raise TokenError("invalid access token") from exc
    if claims.get("type") != "access":
        raise TokenError("invalid token type")
    return cast("dict[str, Any]", claims)
