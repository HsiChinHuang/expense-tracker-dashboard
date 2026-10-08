# mypy: disable-error-code="import-untyped"
"""Integration tests for the auth endpoints (t8, REQ-API-020/021/022).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation is pinned by the groom: every test builds its own SQLite file
under pytest's ``tmp_path``, creates the schema with
``Base.metadata.create_all`` (NOT alembic), and isolates the app through
``dependency_overrides[get_db]``. Unlike t6's helper, these tests
deliberately never read ``DATABASE_URL`` — ac2 runs eight node IDs in one
process and a shared injected file would make them collide.
"""

import base64
import json
from collections.abc import Callable, Generator, Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from jose import jwt as jose_jwt
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.jwt import create_access_token
from app.config import get_settings
from app.database import create_db_engine, create_session_factory, get_db
from app.main import create_app
from app.models.user import Base, User

USER_FIELDS = {"id", "email", "username", "is_active", "created_at"}
ERROR_FIELDS = {"detail", "code", "field"}
TEST_SECRET = "integration-test-secret-not-a-real-key"


@pytest.fixture(autouse=True)
def _pin_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin JWT settings so tokens are issued/verified with test values.

    Teardown clears the settings cache a second time so pinned values
    cannot leak into later tests in the same process (t7 precedent).

    Args:
        monkeypatch: pytest monkeypatch for environment pinning.

    Yields:
        None: Control returns to the test with pinned settings active.
    """
    monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    monkeypatch.setenv("JWT_ISSUER", "expense-tracker")
    monkeypatch.setenv("JWT_AUDIENCE", "expense-tracker-api")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _make_client(
    tmp_path: Path,
) -> tuple[TestClient, Callable[[], Generator[Session, None, None]]]:
    """Build an isolated client over a private tmp-file database.

    Args:
        tmp_path: pytest-provided directory for the SQLite file.

    Returns:
        tuple: A TestClient bound to a fresh app whose ``get_db`` is
        overridden, and the override generator function itself (tests
        mutate rows with ``with next(override()) as session:`` because
        the override is a generator function, not a context manager).
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't8_test.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = create_session_factory(engine)

    def override() -> Generator[Session, None, None]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    application = create_app()
    application.dependency_overrides[get_db] = override
    return TestClient(application), override


def _register(
    client: TestClient,
    email: str = "Alice@Example.com",
    username: str = "alice",
    password: str = "password123",
) -> dict[str, Any]:
    """Register a user and return the parsed 201 body.

    Args:
        client: Isolated test client.
        email: Candidate email (mixed case by default).
        username: Candidate username.
        password: Candidate password.

    Returns:
        dict[str, Any]: The register response body.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert response.status_code == 201
    return cast("dict[str, Any]", response.json())


def _login(
    client: TestClient,
    email: str = "Alice@Example.com",
    password: str = "password123",
) -> dict[str, Any]:
    """Log in and return the parsed 200 body.

    Args:
        client: Isolated test client.
        email: Login email.
        password: Login password.

    Returns:
        dict[str, Any]: The login response body.
    """
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return cast("dict[str, Any]", response.json())


def _unverified_claims(token: str) -> dict[str, Any]:
    """Decode a JWT's payload without verifying the signature.

    Args:
        token: The compact JWT string.

    Returns:
        dict[str, Any]: The unverified claims.
    """
    payload = token.split(".")[1]
    padded = payload + "=" * (-len(payload) % 4)
    return cast("dict[str, Any]", json.loads(base64.urlsafe_b64decode(padded)))


class TestAuthApi:
    """Contract coverage for /api/v1/auth/register|login|me."""

    def test_register_valid_returns_201_lowercase_email_no_password(
        self, tmp_path: Path
    ) -> None:
        """201 body is exactly the five public fields, email lowercased."""
        client, _ = _make_client(tmp_path)

        body = _register(client, email="Alice@Example.com")

        assert set(body.keys()) == USER_FIELDS
        assert body["email"] == "alice@example.com"
        assert body["username"] == "alice"
        assert body["is_active"] is True
        assert isinstance(body["created_at"], str)
        assert not any("password" in key.lower() for key in body)

    def test_register_duplicate_email_case_insensitive_returns_409(
        self, tmp_path: Path
    ) -> None:
        """A case-variant of a stored email is a 409 DUPLICATE_EMAIL."""
        client, _ = _make_client(tmp_path)
        _register(client, email="alice@example.com", username="alice")

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "ALICE@example.COM",
                "username": "different",
                "password": "password123",
            },
        )

        assert response.status_code == 409
        body = response.json()
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "DUPLICATE_EMAIL"
        assert body["field"] == "email"

    def test_register_duplicate_username_case_sensitive_returns_409(
        self, tmp_path: Path
    ) -> None:
        """Exact-case username repeats 409; a different case is accepted."""
        client, _ = _make_client(tmp_path)
        _register(client, email="alice@example.com", username="alice")

        response = client.post(
            "/api/v1/auth/register",
            json={"email": "bob@example.com", "username": "alice", "password": "password123"},
        )

        assert response.status_code == 409
        body = response.json()
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "DUPLICATE_USERNAME"
        assert body["field"] == "username"

        other_case = client.post(
            "/api/v1/auth/register",
            json={"email": "bob@example.com", "username": "ALICE", "password": "password123"},
        )
        assert other_case.status_code == 201

    def test_register_invalid_bodies_return_422_validation_error(
        self, tmp_path: Path
    ) -> None:
        """Each malformed member yields 422 VALIDATION_ERROR with field."""
        client, _ = _make_client(tmp_path)
        invalid_cases: list[tuple[dict[str, str], str]] = [
            ({"email": "not-an-email", "username": "alice", "password": "password123"}, "email"),
            ({"email": "a@b", "username": "alice", "password": "password123"}, "email"),
            ({"email": "a@b.com", "username": "alice", "password": "short7!"}, "password"),
            (
                {"email": "a@b.com", "username": "alice", "password": "p" * 73},
                "password",
            ),
            ({"email": "a@b.com", "username": "ab", "password": "password123"}, "username"),
            ({"email": "a@b.com", "username": "a" * 51, "password": "password123"}, "username"),
            ({"email": "a@b.com", "username": "ali ce", "password": "password123"}, "username"),
        ]

        for payload, expected_field in invalid_cases:
            response = client.post("/api/v1/auth/register", json=payload)

            assert response.status_code == 422, payload
            body = response.json()
            assert set(body.keys()) == ERROR_FIELDS, payload
            assert body["code"] == "VALIDATION_ERROR", payload
            assert body["field"] == expected_field, payload

    def test_login_valid_returns_200_token_user_with_matching_sub(
        self, tmp_path: Path
    ) -> None:
        """Login returns {access_token, token_type, user} with sub == id."""
        client, _ = _make_client(tmp_path)
        registered = _register(client, email="Alice@Example.com")

        body = _login(client, email="alice@example.com")

        assert set(body.keys()) == {"access_token", "token_type", "user"}
        assert body["token_type"] == "bearer"
        assert set(body["user"].keys()) == USER_FIELDS
        assert not any("password" in key.lower() for key in body["user"])
        claims = _unverified_claims(body["access_token"])
        assert claims["sub"] == registered["id"]

    def test_login_wrong_password_and_unknown_email_return_identical_401(
        self, tmp_path: Path
    ) -> None:
        """No-enumeration: both failure bodies are byte-identical (ac2)."""
        client, _ = _make_client(tmp_path)
        _register(client, email="alice@example.com")

        wrong_password = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "wrong-password"},
        )
        unknown_email = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
        )

        assert wrong_password.status_code == 401
        assert unknown_email.status_code == 401
        assert wrong_password.json() == unknown_email.json()
        body = wrong_password.json()
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "INVALID_CREDENTIALS"

    def test_login_inactive_user_returns_401_user_inactive(
        self, tmp_path: Path
    ) -> None:
        """is_active == False blocks login with 401 USER_INACTIVE."""
        client, override = _make_client(tmp_path)
        _register(client, email="alice@example.com")
        with next(override()) as session:
            row = session.query(User).filter_by(email="alice@example.com").one()
            row.is_active = False
            session.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "password123"},
        )

        assert response.status_code == 401
        body = response.json()
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "USER_INACTIVE"

    def test_login_corrupt_stored_hash_returns_401_not_500(self, tmp_path: Path) -> None:
        """Malformed stored hashes 401 INVALID_CREDENTIALS, never 500."""
        client, override = _make_client(tmp_path)
        corrupt_hashes = ["$2b$12$", "$2b$12$short", "$2y$05$" + "a" * 22]

        for index, corrupt in enumerate(corrupt_hashes):
            email = f"victim{index}@example.com"
            _register(client, email=email, username=f"victim{index}")
            with next(override()) as session:
                row = session.query(User).filter_by(email=email).one()
                row.hashed_password = corrupt
                session.commit()

            response = client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": "password123"},
            )

            assert response.status_code == 401, corrupt
            body = response.json()
            assert set(body.keys()) == ERROR_FIELDS
            assert body["code"] == "INVALID_CREDENTIALS"

    def test_me_valid_token_returns_200_current_user(self, tmp_path: Path) -> None:
        """A valid bearer token returns the five public user fields."""
        client, _ = _make_client(tmp_path)
        registered = _register(client, email="Alice@Example.com")
        token = _login(client, email="alice@example.com")["access_token"]

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) == USER_FIELDS
        assert body["id"] == registered["id"]
        assert body["email"] == "alice@example.com"
        assert body["username"] == "alice"

    def test_me_missing_header_returns_401_unauthorized(self, tmp_path: Path) -> None:
        """No Authorization header maps to 401 UNAUTHORIZED (not 403)."""
        client, _ = _make_client(tmp_path)

        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        body = response.json()
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "UNAUTHORIZED"

    def test_me_malformed_and_wrong_signature_return_401_token_invalid(
        self, tmp_path: Path
    ) -> None:
        """Non-JWT strings and wrong-secret signatures map to TOKEN_INVALID."""
        client, _ = _make_client(tmp_path)

        malformed = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt-at-all"}
        )
        forged = jose_jwt.encode(
            {
                "sub": "someone",
                "iss": "expense-tracker",
                "aud": "expense-tracker-api",
                "type": "access",
                "exp": 4102444800,
            },
            "an-entirely-wrong-secret",
            algorithm="HS256",
        )
        wrong_signature = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"}
        )

        for response in (malformed, wrong_signature):
            assert response.status_code == 401
            body = response.json()
            assert set(body.keys()) == ERROR_FIELDS
            assert body["code"] == "TOKEN_INVALID"

    def test_me_expired_token_returns_401_token_expired(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """An expired token maps to TOKEN_EXPIRED, distinct from TOKEN_INVALID."""
        client, _ = _make_client(tmp_path)
        registered = _register(client, email="alice@example.com")
        token = _login(client, email="alice@example.com")["access_token"]

        monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "-1")
        get_settings.cache_clear()
        expired_token = create_access_token(subject=registered["id"])
        monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        get_settings.cache_clear()

        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        body = response.json()
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "TOKEN_EXPIRED"
        assert body["code"] != "TOKEN_INVALID"
        # sanity: the non-expired token from the same user still works
        live = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert live.status_code == 200

    def test_me_valid_token_for_inactive_user_returns_401_user_inactive(
        self, tmp_path: Path
    ) -> None:
        """A valid token for a deactivated account maps to USER_INACTIVE."""
        client, override = _make_client(tmp_path)
        _register(client, email="alice@example.com")
        token = _login(client, email="alice@example.com")["access_token"]
        with next(override()) as session:
            row = session.query(User).filter_by(email="alice@example.com").one()
            row.is_active = False
            session.commit()

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401
        body = response.json()
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "USER_INACTIVE"

    def test_openapi_lists_three_auth_paths_registered_after_health(
        self, tmp_path: Path
    ) -> None:
        """OpenAPI lists the three auth paths and health comes first."""
        client, _ = _make_client(tmp_path)

        schema = client.get("/openapi.json").json()
        paths = list(schema["paths"].keys())

        assert "post" in schema["paths"]["/api/v1/auth/register"]
        assert "post" in schema["paths"]["/api/v1/auth/login"]
        assert "get" in schema["paths"]["/api/v1/auth/me"]
        assert paths.index("/api/v1/health") < paths.index("/api/v1/auth/register")

    def test_register_login_me_end_to_end_flow(self, tmp_path: Path) -> None:
        """register -> login (case-insensitive email) -> me in one flow."""
        client, _ = _make_client(tmp_path)

        registered = _register(client, email="MixedCase@Example.COM", username="flowuser")
        login_body = _login(client, email="mixedcase@example.com")
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_body['access_token']}"},
        )

        assert registered["email"] == "mixedcase@example.com"
        assert set(login_body.keys()) == {"access_token", "token_type", "user"}
        assert me_response.status_code == 200
        assert me_response.json()["id"] == registered["id"]

    def test_health_endpoint_still_returns_200_after_auth_wiring(
        self, tmp_path: Path
    ) -> None:
        """The health router is unaffected by the auth wiring."""
        client, _ = _make_client(tmp_path)

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
