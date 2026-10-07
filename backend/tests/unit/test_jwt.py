# mypy: disable-error-code="import-untyped"
"""Unit tests for the HS256 JWT primitives (t7).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs. JWT
settings are pinned via monkeypatch.setenv + get_settings.cache_clear()
(t5/t6 tmp-isolation precedent) — no .env file, no committed secret —
and the cache is cleared again on teardown so the test settings can
never leak into the t5 config tests in a full-suite run.
"""

import base64
import json
from collections.abc import Iterator
from typing import Any, cast

import pytest
from jose import jwt as jose_jwt

from app.auth.jwt import TokenError, create_access_token, decode_access_token
from app.config import get_settings

TEST_SECRET = "unit-test-secret-not-a-real-key"
TEST_ISSUER = "expense-tracker"
TEST_AUDIENCE = "expense-tracker-api"
SUBJECT = "user-42"


@pytest.fixture(autouse=True)
def _pin_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin JWT settings via environment and clear the settings cache.

    Teardown clears the cache a second time so the pinned test values
    cannot leak into later tests in the same process.

    Args:
        monkeypatch: pytest monkeypatch for environment pinning.

    Yields:
        None: Control returns to the test with pinned settings active.
    """
    monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    monkeypatch.setenv("JWT_ISSUER", TEST_ISSUER)
    monkeypatch.setenv("JWT_AUDIENCE", TEST_AUDIENCE)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _decode_with_test_secret(token: str) -> dict[str, Any]:
    """Decode a token with python-jose directly (library-level checks).

    Args:
        token: The compact JWT string.

    Returns:
        dict[str, Any]: The validated claims.
    """
    claims = jose_jwt.decode(
        token,
        TEST_SECRET,
        algorithms=["HS256"],
        audience=TEST_AUDIENCE,
        issuer=TEST_ISSUER,
    )
    return cast("dict[str, Any]", claims)


class TestJwt:
    """Contract coverage for app.auth.jwt."""

    def test_create_access_token_emits_exact_claim_set_with_24h_expiry(self) -> None:
        """Claims are exactly {sub, iss, aud, iat, exp, type}, exp-iat=86400."""
        token = create_access_token(SUBJECT)
        claims = _decode_with_test_secret(token)
        assert set(claims) == {"sub", "iss", "aud", "iat", "exp", "type"}
        assert claims["sub"] == SUBJECT
        assert claims["type"] == "access"
        assert claims["iss"] == TEST_ISSUER
        assert claims["aud"] == TEST_AUDIENCE
        assert claims["exp"] - claims["iat"] == 1440 * 60

    def test_create_access_token_is_hs256_signed_with_settings_secret(self) -> None:
        """Header is exactly HS256/JWT and a wrong secret is rejected."""
        token = create_access_token(SUBJECT)
        assert jose_jwt.get_unverified_header(token) == {"alg": "HS256", "typ": "JWT"}
        with pytest.raises(jose_jwt.JWTError):
            jose_jwt.decode(
                token,
                "the-wrong-secret",
                algorithms=["HS256"],
                audience=TEST_AUDIENCE,
                issuer=TEST_ISSUER,
            )

    def test_decode_access_token_roundtrips_valid_token(self) -> None:
        """A freshly issued token decodes with its sub intact."""
        token = create_access_token(SUBJECT)
        claims = decode_access_token(token)
        assert claims["sub"] == SUBJECT
        assert claims["type"] == "access"

    def test_decode_rejects_wrong_secret(self) -> None:
        """A token forged with another secret raises TokenError."""
        settings = get_settings()
        forged = jose_jwt.encode(
            {
                "sub": SUBJECT,
                "iss": settings.JWT_ISSUER,
                "aud": settings.JWT_AUDIENCE,
                "type": "access",
            },
            "attacker-secret",
            algorithm="HS256",
        )
        with pytest.raises(TokenError):
            decode_access_token(cast(str, forged))

    def test_decode_rejects_tampered_signature(self) -> None:
        """Flipping one signature character raises TokenError."""
        token = create_access_token(SUBJECT)
        head, _, signature = token.partition(".")
        flipped = ("A" if signature[0] != "A" else "B") + signature[1:]
        with pytest.raises(TokenError):
            decode_access_token(f"{head}.{flipped}")

    def test_decode_rejects_expired_token(self) -> None:
        """A token issued with negative lifetime raises TokenError."""
        with pytest.MonkeyPatch.context() as expired_patch:
            expired_patch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "-1")
            get_settings.cache_clear()
            token = create_access_token(SUBJECT)
            with pytest.raises(TokenError):
                decode_access_token(token)
        get_settings.cache_clear()

    def test_decode_rejects_wrong_audience(self) -> None:
        """A token minted for another audience raises TokenError."""
        settings = get_settings()
        forged = jose_jwt.encode(
            {
                "sub": SUBJECT,
                "iss": settings.JWT_ISSUER,
                "aud": "some-other-api",
                "type": "access",
            },
            settings.JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(TokenError):
            decode_access_token(cast(str, forged))

    def test_decode_rejects_wrong_issuer(self) -> None:
        """A token minted by another issuer raises TokenError."""
        settings = get_settings()
        forged = jose_jwt.encode(
            {
                "sub": SUBJECT,
                "iss": "some-other-issuer",
                "aud": settings.JWT_AUDIENCE,
                "type": "access",
            },
            settings.JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(TokenError):
            decode_access_token(cast(str, forged))

    def test_decode_rejects_refresh_type_token(self) -> None:
        """A token with type == 'refresh' raises TokenError."""
        settings = get_settings()
        forged = jose_jwt.encode(
            {
                "sub": SUBJECT,
                "iss": settings.JWT_ISSUER,
                "aud": settings.JWT_AUDIENCE,
                "type": "refresh",
            },
            settings.JWT_SECRET,
            algorithm="HS256",
        )
        with pytest.raises(TokenError):
            decode_access_token(cast(str, forged))

    def test_decode_rejects_alg_none_forgery(self) -> None:
        """A hand-built alg=none token raises TokenError (REQ-BE-022)."""

        def b64url(raw: bytes) -> str:
            return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

        settings = get_settings()
        header = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode("ascii"))
        payload = b64url(
            json.dumps(
                {
                    "sub": SUBJECT,
                    "iss": settings.JWT_ISSUER,
                    "aud": settings.JWT_AUDIENCE,
                    "type": "access",
                }
            ).encode("ascii")
        )
        with pytest.raises(TokenError):
            decode_access_token(f"{header}.{payload}.")
