"""Integration tests for the live SQLite fallback surface (t25 ac3/ac4/ac5).

Node IDs are part of the issue contract: the AC verification commands
reference these exact pytest node IDs. ``with TestClient(create_app())``
— the context manager that runs the startup handler — appears ONLY in
this file and its unit sibling (issue state-hygiene pin): every merged
bare-``TestClient(create_app())`` test stays untouched and database-free
because the engine is created only inside the startup handler.

JWT settings are pinned per the merged t8/t13 fixture pattern and the
cwd is moved to ``tmp_path`` so the ``./fallback.db`` target is private
to each node. Evidence lines are APPENDED to the shared gitignored
``tests/sqlite_fallback_evidence.txt`` on success only, via absolute
paths (these nodes ``monkeypatch.chdir``).
"""

from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from sqlalchemy import Engine, func, inspect, select
from sqlalchemy.orm import Session, sessionmaker

from app import database
from app.config import get_settings
from app.database import create_session_factory
from app.main import create_app
from app.models import Base
from app.models.category import Category
from app.models.user import User  # noqa: TC001 (runtime ORM registration)

REFUSED_URL = "postgresql+psycopg://t25:t25@127.0.0.1:1/t25_probe"
EVIDENCE = (Path(__file__).parent.parent / "sqlite_fallback_evidence.txt").as_posix()
TEST_SECRET = "sqlite-fallback-integration-secret-not-a-real-key"
EXPECTED_FIELDS = {"status", "database", "fallback_active", "version"}


def _record(line: str) -> None:
    """Append one evidence line to the shared evidence file.

    Args:
        line: The full line (ending ``rc=0``) to append.
    """
    with Path(EVIDENCE).open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _reset_state(monkeypatch: MonkeyPatch) -> None:
    """Clear the latched flag and the settings cache (leak guard).

    Args:
        monkeypatch: pytest monkeypatch for the flag reset.
    """
    monkeypatch.setattr(database, "IS_FALLBACK", False)
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _pin_jwt_settings(monkeypatch: MonkeyPatch) -> Generator[None, None, None]:
    """Pin JWT settings and reset fallback state around every node.

    Args:
        monkeypatch: pytest monkeypatch for environment pinning.

    Yields:
        Generator[None, None, None]: Control returns to the test with
        pinned settings and an unlatched fallback flag.
    """
    monkeypatch.setenv("JWT_SECRET", TEST_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    monkeypatch.setenv("JWT_ISSUER", "expense-tracker")
    monkeypatch.setenv("JWT_AUDIENCE", "expense-tracker-api")
    _reset_state(monkeypatch)
    yield
    _reset_state(monkeypatch)


def _override_factory(
    engine: Engine,
) -> Callable[[], Generator[Session, None, None]]:
    """Build a ``get_db`` override bound to ``engine``.

    Args:
        engine: Engine the request sessions will use.

    Returns:
        Callable: Generator function for ``dependency_overrides``.
    """
    factory: sessionmaker[Session] = create_session_factory(engine)

    def override() -> Generator[Session, None, None]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    return override


def _fallback_client(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> TestClient:
    """Build a client whose startup falls back to a private SQLite file.

    The startup handler writes ``./fallback.db`` — which resolves into
    ``tmp_path`` because of the chdir — so the ``get_db`` override
    binds the SAME file: request sessions and startup initialization
    share one private database per node.

    Args:
        tmp_path: pytest directory holding the private fallback file.
        monkeypatch: pytest monkeypatch for cwd/env/flag resets.

    Returns:
        TestClient: Client NOT yet started; the caller enters the
        context manager to trigger the startup fallback.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", REFUSED_URL)
    get_settings.cache_clear()
    application = create_app()
    application.dependency_overrides[database.get_db] = _override_factory(
        database._sqlite_engine(f"sqlite:///{(tmp_path / 'fallback.db').as_posix()}")
    )
    return TestClient(application)


def _sqlite_client(tmp_path: Path, monkeypatch: MonkeyPatch) -> TestClient:
    """Build a client configured with a plain SQLite URL (no fallback).

    Args:
        tmp_path: pytest directory holding the SQLite file.
        monkeypatch: pytest monkeypatch for cwd/env resets.

    Returns:
        TestClient: Client NOT yet started.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'plain.db').as_posix()}")
    get_settings.cache_clear()
    return TestClient(create_app())


def _count(engine: Engine, model: Any) -> int:
    """Count rows of ``model`` through a fresh connection.

    Args:
        engine: Engine to query.
        model: ORM model class to count.

    Returns:
        int: The row count.
    """
    with engine.connect() as conn:
        return int(
            conn.scalar(select(func.count()).select_from(inspect(model).local_table))
            or 0
        )


def _register(client: TestClient, email: str) -> None:
    """Register a user through the real endpoint (201 asserted).

    Args:
        client: Started test client.
        email: Candidate email.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": email.split("@")[0], "password": "password123"},
    )
    assert response.status_code == 201


def _login(client: TestClient, email: str) -> str:
    """Log in and return the access token (200 asserted).

    Args:
        client: Started test client.
        email: Account email.

    Returns:
        str: The JWT access token.
    """
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "password123"}
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _auth(token: str) -> dict[str, str]:
    """Return bearer headers.

    Args:
        token: JWT access token.

    Returns:
        dict[str, str]: Headers for the TestClient call.
    """
    return {"Authorization": f"Bearer {token}"}


def test_health_reports_degraded_sqlite_true_when_fallback_is_active(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Startup fallback: health honestly reports degraded/sqlite/true."""
    client = _fallback_client(tmp_path, monkeypatch)

    with client:
        body = client.get("/api/v1/health").json()

    assert body["status"] == "degraded"
    assert body["database"] == "sqlite"
    assert body["fallback_active"] is True
    assert database.is_fallback() is True
    _record("HEALTH_FALLBACK degraded/sqlite/true rc=0")

def test_health_reports_ok_sqlite_false_for_a_plain_sqlite_app(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Plain SQLite config: ok/sqlite/false, no fallback ever latched."""
    client = _sqlite_client(tmp_path, monkeypatch)

    with client:
        body = client.get("/api/v1/health").json()

    assert body["status"] == "ok"
    assert body["database"] == "sqlite"
    assert body["fallback_active"] is False
    assert database.is_fallback() is False
    _record("HEALTH_PLAIN ok/sqlite/false rc=0")

def test_health_body_keeps_exactly_the_four_documented_fields(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Both states keep the body keys at exactly the four fields."""
    fallback_client = _fallback_client(tmp_path, monkeypatch)
    with fallback_client:
        fallback_body = fallback_client.get("/api/v1/health").json()

    plain_client = _sqlite_client(tmp_path, monkeypatch)
    with plain_client:
        plain_body = plain_client.get("/api/v1/health").json()

    assert set(fallback_body.keys()) == EXPECTED_FIELDS
    assert set(plain_body.keys()) == EXPECTED_FIELDS
    _record("HEALTH_FOUR_FIELDS exactly-4 rc=0")

def test_all_merged_endpoints_answer_their_contracts_while_fallback_is_active(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """register/login/expense/budget/health all work in fallback."""
    client = _fallback_client(tmp_path, monkeypatch)

    with client:
        _register(client, "e2e@example.test")
        token = _login(client, "e2e@example.test")
        categories = client.get("/api/v1/categories", headers=_auth(token))
        assert categories.status_code == 200
        food = next(
            row
            for row in categories.json()["categories"]
            if row["name"] == "Food & Dining"
        )
        expense = client.post(
            "/api/v1/expenses",
            json={
                "amount": "42.10",
                "category_id": food["id"],
                "date": "2026-01-15",
                "note": "fallback shop",
            },
            headers=_auth(token),
        )
        budget = client.put(
            "/api/v1/budgets/2026-01",
            json={"amount": "1000.00"},
            headers=_auth(token),
        )
        health = client.get("/api/v1/health")

    codes = (
        f"register=201 login=200 expense={expense.status_code} "
        f"budget={budget.status_code} health={health.status_code}"
    )
    assert expense.status_code == 201
    assert budget.status_code == 200
    assert health.status_code == 200
    assert health.json()["fallback_active"] is True
    _record(f"FALLBACK_ENDPOINTS {codes} rc=0")

def test_restart_during_fallback_rebuilds_an_empty_but_seeded_database(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Deleting fallback.db (container restart) rebuilds empty+seeded."""
    client = _fallback_client(tmp_path, monkeypatch)

    with client:
        _register(client, "restart@example.test")
        token = _login(client, "restart@example.test")
        categories = client.get("/api/v1/categories", headers=_auth(token))
        food = next(
            row
            for row in categories.json()["categories"]
            if row["name"] == "Food & Dining"
        )
        client.post(
            "/api/v1/expenses",
            json={
                "amount": "10.00",
                "category_id": food["id"],
                "date": "2026-01-15",
                "note": "gone on restart",
            },
            headers=_auth(token),
        )

    probe = database._sqlite_engine(
        f"sqlite:///{(tmp_path / 'fallback.db').as_posix()}"
    )
    assert _count(probe, User) == 1
    probe.dispose()
    # container restart: the fallback file is ephemeral
    (tmp_path / "fallback.db").unlink()

    _reset_state(monkeypatch)
    restart = _fallback_client(tmp_path, monkeypatch)
    with restart:
        login = restart.post(
            "/api/v1/auth/login",
            json={"email": "restart@example.test", "password": "password123"},
        )
        users_probe = database._sqlite_engine(
            f"sqlite:///{(tmp_path / 'fallback.db').as_posix()}"
        )
        users = _count(users_probe, User)
        categories_left = _count(users_probe, Category)
        users_probe.dispose()
        _register(restart, "fresh@example.test")
        fresh_token = _login(restart, "fresh@example.test")
        rebuilt = restart.get("/api/v1/categories", headers=_auth(fresh_token))

    assert rebuilt.status_code == 200
    assert len(rebuilt.json()["categories"]) == 10
    assert login.status_code == 401
    assert users == 0
    assert categories_left == 10
    _record(f"FALLBACK_RESTART users={users} categories={categories_left} rc=0")

def test_startup_without_fallback_initializes_no_schema_and_seeds_nothing(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Primary startup path: no create_all, no seed — Alembic owns it."""
    monkeypatch.chdir(tmp_path)
    url = f"sqlite:///{(tmp_path / 'none.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()

    def _forbidden(*args: Any, **kwargs: Any) -> None:
        msg = "primary startup must never create_all (Alembic owns schema)"
        raise AssertionError(msg)

    monkeypatch.setattr(type(Base.metadata), "create_all", _forbidden)

    with TestClient(create_app()):
        pass

    assert database.is_fallback() is False
    probe = database._sqlite_engine(url)
    assert inspect(probe).get_table_names() == []
    probe.dispose()
    _record("FALLBACK_STARTUP_PRIMARY users=0 categories=0 rc=0")
