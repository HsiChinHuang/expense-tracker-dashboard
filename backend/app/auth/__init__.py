"""Auth primitives package (t7).

Re-exports the password and JWT helpers so t8's auth service imports
from ``app.auth`` rather than the individual modules.
"""

from app.auth.jwt import TokenError, create_access_token, decode_access_token
from app.auth.password import hash_password, verify_dummy, verify_password

__all__ = [
    "TokenError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_dummy",
    "verify_password",
]
