"""JWT verification and API-token access for the MCP server (REQ-AI-083, REQ-EXT-033).

``verify_jwt`` is the MCP-side mirror of the backend's dependency: it validates
the signature, the expiry (``python-jose`` checks ``exp`` by default on decode),
the audience, the issuer and the ``type == "access"`` claim, then returns the
``sub`` claim. ``get_user_token`` supplies the bearer token the server presents
to the API.

Every failure path raises :class:`AuthError` -- the code never swallows a
failure behind a broad handler, and it never reaches for a database or the
backend application: the agent authenticates and then calls the API
(REQ-AI-087, REQ-EXT-030, REQ-ARCH-002).
"""

from typing import Any

from config import JWT_ALGORITHM, JWT_AUDIENCE, JWT_ISSUER, MCP_JWT_SECRET, MCP_USER_TOKEN
from jose import JWTError, jwt


class AuthError(Exception):
    """Raised for every authentication failure (never a silent fallback)."""


def verify_jwt(token: str) -> str:
    """Validate *token* and return the authenticated subject.

    Args:
        token: Compact JWS access token minted by the backend auth routes.

    Returns:
        str: The ``sub`` claim (the user id) of a valid access token.

    Raises:
        AuthError: Signature, expiry, audience, issuer or ``type`` validation
            failed, or the token carries no subject.
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            MCP_JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
        )
    except JWTError as exc:
        raise AuthError(f"token rejected: {exc}") from exc

    if payload.get("type") != "access":
        raise AuthError("token is not an access token")

    subject = payload.get("sub")
    if subject is None or subject == "":
        raise AuthError("token carries no subject")

    return str(subject)


def get_user_token() -> str:
    """Return the bearer token the server presents to the backend API.

    Returns:
        str: The configured ``MCP_USER_TOKEN`` value.

    Raises:
        AuthError: The token is missing, so no API call can be authenticated.
    """
    token = MCP_USER_TOKEN
    if not token:
        raise AuthError("MCP_USER_TOKEN is not configured")
    return token
