"""Unit tests for the auth service (t8, REQ-BE-050/051, REQ-SEC-022/023).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation follows the groom pin: every test builds its own SQLite file
under ``tmp_path`` with ``Base.metadata.create_all`` and never reads
``DATABASE_URL`` (ac2 runs several nodes in one process). The service is
called directly — no HTTP layer here; that is the integration module.

The timing-parity requirement (REQ-SEC-023) is pinned as a code-path
assertion via monkeypatch spies on ``verify_dummy``: called exactly once
with the candidate password on the unknown-email path, zero times on the
wrong-password path. Wall-clock bounds live in t7's ac2 at the primitive
level and are deliberately not re-measured here.
"""

# mypy: disable-error-code="import-untyped"

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from jose import jwt as jose_jwt
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import password as password_module
from app.config import get_settings
from app.core.errors import INVALID_CREDENTIALS, AppError
from app.database import create_db_engine, create_session_factory
from app.models.user import Base, User
from app.services import auth_service
from app.services.auth_service import (
    authenticate_user,
    email_identifier,
    login_user,
    register_user,
)

TEST_SECRET = "unit-test-secret-not-a-real-key"
PASSWORD = "password123"


@pytest.fixture(autouse=True)
def _pin_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin JWT settings via environment and clear the settings cache.

    Teardown clears the cache a second time so pinned values cannot leak
    into later tests in the same process (t7 precedent).

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


def _session(tmp_path: Path) -> Session:
    """Create the schema on a private tmp-file engine and open a Session.

    Args:
        tmp_path: pytest-provided directory for the SQLite file.

    Returns:
        Session: A session over a database containing the users table.
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't8_unit.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = create_session_factory(engine)
    return factory()


class _DummySpy:
    """Callable spy recording verify_dummy invocations."""

    def __init__(self) -> None:
        """Start with an empty call log."""
        self.calls: list[str] = []

    def __call__(self, plain: str) -> None:
        """Record the candidate password without doing bcrypt work.

        Args:
            plain: The candidate password the service passed in.
        """
        self.calls.append(plain)


def _spy_verify_dummy(monkeypatch: pytest.MonkeyPatch) -> _DummySpy:
    """Replace ``verify_dummy`` in BOTH import sites with one spy.

    The service imports the symbol directly (``from app.auth.password
    import verify_dummy``), so both the source module and the service
    module attribute are patched to keep the spy honest.

    Args:
        monkeypatch: pytest monkeypatch for the replacements.

    Returns:
        _DummySpy: The installed spy.
    """
    spy = _DummySpy()
    monkeypatch.setattr(password_module, "verify_dummy", spy)
    monkeypatch.setattr(auth_service, "verify_dummy", spy)
    return spy


class TestAuthService:
    """Contract coverage for register/login/authenticate."""

    def test_login_valid_returns_user_and_token_with_sub_user_id(
        self, tmp_path: Path
    ) -> None:
        """login_user returns the row plus a JWT whose sub is str(user.id)."""
        session = _session(tmp_path)
        user = register_user(session, "Alice@Example.com", "alice", PASSWORD)

        result = login_user(session, "alice@example.com", PASSWORD)

        assert result.user.id == user.id
        claims = cast(
            "dict[str, Any]",
            jose_jwt.get_unverified_claims(result.access_token),
        )
        assert claims["sub"] == str(user.id)
        session.close()

    def test_login_unknown_email_invokes_verify_dummy(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Unknown email pays exactly one dummy verify with the password."""
        session = _session(tmp_path)
        register_user(session, "alice@example.com", "alice", PASSWORD)
        spy = _spy_verify_dummy(monkeypatch)

        with pytest.raises(AppError) as excinfo:
            authenticate_user(session, "nobody@example.com", PASSWORD)

        assert excinfo.value.status_code == 401
        assert excinfo.value.code == INVALID_CREDENTIALS
        assert spy.calls == [PASSWORD]
        session.close()

    def test_login_wrong_password_does_not_invoke_verify_dummy(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The wrong-password path verifies the real hash, never the decoy."""
        session = _session(tmp_path)
        register_user(session, "alice@example.com", "alice", PASSWORD)
        spy = _spy_verify_dummy(monkeypatch)

        with pytest.raises(AppError) as excinfo:
            authenticate_user(session, "alice@example.com", "wrong-password")

        assert excinfo.value.status_code == 401
        assert excinfo.value.code == INVALID_CREDENTIALS
        assert spy.calls == []
        session.close()

    def test_login_corrupt_stored_hash_raises_invalid_credentials_not_value_error(
        self, tmp_path: Path
    ) -> None:
        """t7 carry-forward #1: all three malformed shapes map to 401.

        passlib 1.7.4 / bcrypt 4.0.1 raise plain ValueError (not
        UnknownHashError) for these; the service-layer catch converts
        them into AppError 401 INVALID_CREDENTIALS instead of a 500.
        """
        session = _session(tmp_path)
        corrupt_hashes = ["$2b$12$", "$2b$12$short", "$2y$05$" + "a" * 22]

        for index, corrupt_hash in enumerate(corrupt_hashes):
            email = f"victim{index}@example.com"
            user = register_user(session, email, f"victim{index}", PASSWORD)
            user.hashed_password = corrupt_hash
            session.commit()

            with pytest.raises(AppError) as excinfo:
                authenticate_user(session, email, PASSWORD)

            assert excinfo.value.status_code == 401, corrupt_hash
            assert excinfo.value.code == INVALID_CREDENTIALS
        session.close()

    def test_failed_login_logs_no_raw_email_and_no_password(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Failure records leak neither raw email (any case) nor password."""
        session = _session(tmp_path)
        email = "Target.User@Example.com"
        password = "SuperSecret99!"

        with caplog.at_level(logging.DEBUG, logger="app.services.auth_service"):
            with pytest.raises(AppError) as excinfo:
                authenticate_user(session, email, password)

        assert excinfo.value.code == INVALID_CREDENTIALS
        records = [r for r in caplog.records if r.name == "app.services.auth_service"]
        assert records, "expected at least one service log record"
        for record in records:
            rendered = record.getMessage()
            assert password not in rendered
            assert email.lower() not in rendered
            assert email not in rendered
            for value in vars(record).values():
                assert password not in str(value)
                assert email.lower() not in str(value).lower()
            assert email_identifier(email.lower()) in str(vars(record))
        session.close()

    def test_register_and_login_success_log_events_without_secrets(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """auth.register and auth.login events carry no secrets."""
        email = "Quiet@Example.com"
        password = "AnotherSecret9"
        session = _session(tmp_path)

        with caplog.at_level(logging.DEBUG, logger="app.services.auth_service"):
            register_user(session, email, "quiet", password)
            login_user(session, email, password)

        rendered_records = [
            r for r in caplog.records if r.name == "app.services.auth_service"
        ]
        events = {r.getMessage() for r in rendered_records}
        assert {"auth.register", "auth.login"} <= events

        stored_hash = session.execute(
            select(User).where(User.email == "quiet@example.com")
        ).scalar_one().hashed_password
        for record in rendered_records:
            rendered = record.getMessage()
            assert password not in rendered
            assert email.lower() not in rendered
            assert email not in rendered
            assert stored_hash not in rendered
            for value in vars(record).values():
                assert password not in str(value)
                assert email.lower() not in str(value).lower()
                assert stored_hash not in str(value)
        session.close()
