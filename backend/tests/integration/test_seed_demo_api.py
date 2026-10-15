"""API tests for the seeded demo account (t65 ac2).

Class and function names are part of the issue contract: the ac2
verification command in docs/issues/t65.md runs these exact pytest
node IDs. The API leg needs ``TestClient`` with
``dependency_overrides[get_db]`` (the merged t8/t11 precedent), which
is why these tests live in the integration directory — the card's
conditional file (4) trigger.

Isolation contract (t8 precedent): every test builds its own SQLite
file under pytest's ``tmp_path`` and isolates the app through
``dependency_overrides[get_db]``; ``os.environ["DATABASE_URL"]`` is
never read. The anchor is pinned per test so the dashboard month the
tests query never depends on the wall clock.
"""

from datetime import date
from pathlib import Path
from typing import Any, cast

from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import create_db_engine, create_session_factory, get_db
from app.main import create_app
from app.models import Base
from app.scripts.seed_demo import DEMO_EMAIL, DEMO_PASSWORD, seed_demo_data

ANCHOR = date(2026, 10, 15)
"""Fixed anchor so the queried dashboard month is deterministic."""

ANCHOR_MONTH = "2026-10"
"""The ``year_month`` every dashboard query in this module uses."""


def _client(tmp_path: Path, name: str) -> TestClient:
    """Build an isolated client over a seeded private SQLite file.

    Args:
        tmp_path: pytest-provided directory for the SQLite file.
        name: Test-specific file name so no two tests share a file.

    Returns:
        TestClient: A client whose ``get_db`` is overridden onto the
            demo-seeded database (schema via ``create_all``, seed via
            the module under test).
    """
    engine: Engine = create_db_engine(
        f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}"
    )
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = create_session_factory(engine)
    with factory() as seed_session:
        with seed_session.begin():
            seed_demo_data(seed_session.connection(), anchor=ANCHOR)

    def override() -> Any:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    application = create_app()
    application.dependency_overrides[get_db] = override
    return TestClient(application)


class TestSeedDemoApi:
    """Contract coverage for the demo account through the API (t65 ac2)."""

    def test_demo_login_returns_token_and_dashboard_has_data(
        self, tmp_path: Path
    ) -> None:
        """The pinned credentials log in and the anchor month surfaces money."""
        client = _client(
            tmp_path, "test_demo_login_returns_token_and_dashboard_has_data"
        )
        login = client.post(
            "/api/v1/auth/login",
            json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        )
        assert login.status_code == 200
        token = cast("dict[str, Any]", login.json())["access_token"]
        assert isinstance(token, str) and len(token) > 20
        headers = {"Authorization": f"Bearer {token}"}

        summary = client.get(
            "/api/v1/dashboard/summary",
            params={"year_month": ANCHOR_MONTH},
            headers=headers,
        )
        assert summary.status_code == 200
        body = cast("dict[str, Any]", summary.json())
        assert len(str(body["total"]).split(".")[1]) == 2
        assert float(body["total"]) > 0

        grouped = client.get(
            "/api/v1/dashboard/by-category",
            params={"year_month": ANCHOR_MONTH},
            headers=headers,
        )
        assert grouped.status_code == 200
        rows = cast("dict[str, Any]", grouped.json())["categories"]
        assert len(rows) > 0
        assert all(len(str(row["amount"]).split(".")[1]) == 2 for row in rows)

    def test_wrong_password_for_demo_account_is_401(self, tmp_path: Path) -> None:
        """The demo login leg proves it bites: a wrong password is 401."""
        client = _client(tmp_path, "test_wrong_password_for_demo_account_is_401")
        response = client.post(
            "/api/v1/auth/login",
            json={"email": DEMO_EMAIL, "password": "demo-wrong-password-9"},
        )
        assert response.status_code == 401
