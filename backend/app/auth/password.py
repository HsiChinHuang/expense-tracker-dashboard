# mypy: disable-error-code="import-untyped"
"""bcrypt password hashing primitives (t7, REQ-BE-030/REQ-SEC-020).

A single module-level passlib ``CryptContext`` owns the bcrypt policy
(rounds=12) so callers never touch the ``bcrypt`` package directly.
The module is pure crypto: it imports nothing from ``app.*``.
"""

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

_CONTEXT = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
"""Shared bcrypt context: cost 12, automatic per-hash salts (REQ-SEC-020)."""

_DUMMY_HASH = _CONTEXT.hash("t7-dummy-decoy-secret")
"""Fixed decoy hash materialized at import time at the context's cost-12
policy. It is a decoy for the timing-attack mitigation only — it is never
compared against real user input and guards no secret (REQ-BE-032)."""


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt cost 12 (REQ-BE-030).

    Args:
        plain: The plaintext password to hash.

    Returns:
        str: A 60-character ``$2b$12$...`` bcrypt hash with a fresh
            random salt, so hashing the same input twice yields
            different strings.
    """
    result = _CONTEXT.hash(plain)
    assert isinstance(result, str)
    return result


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash.

    Args:
        plain: The candidate plaintext password.
        hashed: The stored bcrypt hash.

    Returns:
        bool: ``True`` when ``plain`` matches ``hashed``, ``False``
            otherwise — including for malformed or empty stored hashes,
            which never raise (REQ-BE-030).
    """
    try:
        return bool(_CONTEXT.verify(plain, hashed))
    except UnknownHashError:
        return False


def verify_dummy(plain: str) -> None:
    """Run a full cost-12 bcrypt verification against the fixed decoy.

    Callers use this on unknown-user logins so an unknown account costs
    the same wall-clock time as a wrong-password login, closing the
    user-enumeration timing channel (REQ-BE-032/REQ-SEC-023). The
    ``plain`` argument is intentionally never compared against the
    decoy hash; the point is the verification cost, not the result.

    Args:
        plain: The candidate password (unused; present for call-site
            symmetry with :func:`verify_password`).
    """
    _CONTEXT.verify(plain, _DUMMY_HASH)
