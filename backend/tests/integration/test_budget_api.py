"""Integration tests for /api/v1/budgets (t14 ac2..ac4, ac6, REQ-API-050..052).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

The harness is a COPY of the merged t13 pattern from
tests/integration/test_expense_api.py (there is no tests/conftest.py and
no cross-test-module imports). Isolation follows the groom pin: one
private SQLite file PER TEST under ``tmp_path``, schema via
``Base.metadata.create_all`` (NOT alembic), app isolation through
``dependency_overrides[get_db]``. Cross-user cases register TWO real
users through the real register endpoint.

Wire-behavior pins exercised here (review_plan W8, FROZEN):
malformed year_month formats are 422 VALIDATION_ERROR on EVERY route
(never 404, never the "0.00" body) while a well-formed ABSENT month is
the exact 200 body ``{"year_month": <echo>, "amount": "0.00"}`` — the
two cases never collapse. PUT is upsert: 200 for create AND update,
never 201; no 409 DUPLICATE_BUDGET path exists (the DB UNIQUE proved in
ac1 is the guard).
"""

import re
import uuid
from collections.abc import Callable, Generator, Iterator
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.database import create_db_engine, create_session_factory, get_db
from app.main import create_app
from app.models import Base
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.scripts.seed import seed_system_categories

BUDGET_FIELDS = {"year_month", "amount"}
ERROR_FIELDS = {"detail", "code", "field"}
TWO_DP = re.compile(r"^[0-9]+\.[0-9]{2}$")
MALFORMED_MONTHS = ("2026-1", "2026-13", "2026-1-01", "abcd-ef")
TEST_SECRET = "budgets-integration-secret-not-a-real-key"


@pytest.fixture(autouse=True)
def _pin_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin JWT settings so tokens are issued/verified with test values.

    Teardown clears the settings cache a second time so pinned values
    cannot leak into later tests in the same process (t8/t13 precedent).

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
        tuple: A TestClient whose ``get_db`` is overridden, and the
        override generator function itself (fresh-session probes run
        ``with next(override()) as session:``).
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't14_test.db').as_posix()}")
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


def _seed(override: Callable[[], Generator[Session, None, None]]) -> None:
    """Provision the ten system categories through the merged seed.

    Args:
        override: The ``get_db`` override generator function.
    """
    with next(override()) as session:
        seed_system_categories(session.connection())
        session.commit()


def _register(client: TestClient, email: str, username: str) -> None:
    """Register a user through the real register endpoint.

    Args:
        client: Isolated test client.
        email: Candidate email.
        username: Candidate username.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "password123"},
    )
    assert response.status_code == 201


def _login(client: TestClient, email: str) -> str:
    """Log in and return the access token string.

    Args:
        client: Isolated test client.
        email: Account email.

    Returns:
        str: The JWT access token.
    """
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    return cast("str", cast("dict[str, Any]", response.json())["access_token"])


def _auth(token: str) -> dict[str, str]:
    """Return bearer headers.

    Args:
        token: JWT access token.

    Returns:
        dict[str, str]: Headers for the TestClient call.
    """
    return {"Authorization": f"Bearer {token}"}


def _put(client: TestClient, token: str, month: str, amount: str) -> Any:
    """PUT /api/v1/budgets/{month} and return the raw response.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        month: year_month path value.
        amount: Body amount string.

    Returns:
        Any: The httpx Response object.
    """
    return client.put(
        f"/api/v1/budgets/{month}", json={"amount": amount}, headers=_auth(token)
    )


def _budget_rows(
    override: Callable[[], Generator[Session, None, None]]
) -> list[tuple[str, Decimal]]:
    """Return every persisted (year_month, amount) through a FRESH session.

    Args:
        override: The ``get_db`` override generator function.

    Returns:
        list[tuple[str, Decimal]]: Sorted (month, quantized amount) pairs.
    """
    with next(override()) as session:
        rows = session.scalars(select(Budget)).all()
        return sorted(
            (row.year_month, row.amount.quantize(Decimal("0.01"))) for row in rows
        )


def _budget_count(override: Callable[[], Generator[Session, None, None]]) -> int:
    """Count ALL budget rows through a FRESH session.

    Args:
        override: The ``get_db`` override generator function.

    Returns:
        int: Number of budget rows in the database.
    """
    with next(override()) as session:
        return int(session.scalar(select(func.count()).select_from(Budget)) or 0)


class TestBudgetPut:
    """Contract coverage for PUT /api/v1/budgets/{year_month} (t14 ac2)."""

    def test_put_creates_budget_with_exactly_the_two_frozen_response_keys(
        self, tmp_path: Path
    ) -> None:
        """First PUT creates and answers 200 with EXACTLY two keys."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        response = _put(client, token, "2026-10", "2000.00")

        assert response.status_code == 200
        assert response.status_code != 201  # upsert never answers 201
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == BUDGET_FIELDS
        assert body["year_month"] == "2026-10"  # echoes the path
        assert body["amount"] == "2000.00"
        assert _budget_rows(override) == [("2026-10", Decimal("2000.00"))]

    def test_second_put_replaces_amount_and_row_count_stays_one(
        self, tmp_path: Path
    ) -> None:
        """Upsert: a second PUT REPLACES the amount, no duplicate row."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        assert _put(client, token, "2026-10", "2000.00").status_code == 200

        second = _put(client, token, "2026-10", "2500.50")

        assert second.status_code == 200
        body = cast("dict[str, Any]", second.json())
        assert body["amount"] == "2500.50"
        # fresh session: EXACTLY one row for that user/month, NEW amount
        assert _budget_count(override) == 1
        assert _budget_rows(override) == [("2026-10", Decimal("2500.50"))]

    def test_put_amount_is_a_two_dp_string_never_a_json_float(
        self, tmp_path: Path
    ) -> None:
        """amount is a quoted 2-dp string in the RAW JSON, not a number."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        response = _put(client, token, "2026-10", "2000.5")

        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert isinstance(body["amount"], str)
        assert TWO_DP.match(body["amount"]), body["amount"]
        assert body["amount"] == "2000.50"
        compact = response.text.replace(" ", "")
        assert '"amount":"2000.50"' in compact, response.text
        assert '"amount":2000.5' not in compact, response.text

    def test_put_invalid_amount_values_return_422_invalid_amount_field_amount(
        self, tmp_path: Path
    ) -> None:
        """The five frozen amount-VALUE cases all render INVALID_AMOUNT."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        for bad in ("0", "-1", "1.234", "10000000000.00", ""):
            response = _put(client, token, "2026-10", bad)

            assert response.status_code == 422, bad
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS, bad
            assert body["code"] == "INVALID_AMOUNT", bad
            assert body["field"] == "amount", bad
        assert _budget_count(override) == 0  # NOTHING persisted

    def test_put_missing_amount_non_string_or_extra_key_return_422_validation_error(
        self, tmp_path: Path
    ) -> None:
        """Structural body failures render VALIDATION_ERROR, never persist."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        bodies: list[dict[str, Any]] = [
            {},  # missing amount key
            {"amount": 5},  # non-string amount
            {"amount": "1.00", "year_month": "2026-10"},  # unknown extra key
        ]
        for payload in bodies:
            response = client.put(
                "/api/v1/budgets/2026-10", json=payload, headers=_auth(token)
            )

            assert response.status_code == 422, payload
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS, payload
            assert body["code"] == "VALIDATION_ERROR", payload
        assert _budget_count(override) == 0

    def test_malformed_year_month_paths_return_422_never_404_never_zero_body(
        self, tmp_path: Path
    ) -> None:
        """W8 FROZEN: all four malformed forms are 422 VALIDATION_ERROR.

        Never 404, never the absent-month "0.00" body, on every PUT;
        INVALID_MONTH is not the wire code on this path.
        """
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        for month in MALFORMED_MONTHS:
            response = _put(client, token, month, "2000.00")

            assert response.status_code == 422, month
            assert response.status_code != 404, month
            body = cast("dict[str, Any]", response.json())
            assert "detail" in body, month
            assert body["code"] == "VALIDATION_ERROR", month
            assert body["field"] == "year_month", month
        assert _budget_count(override) == 0


class TestBudgetGet:
    """Contract coverage for GET /api/v1/budgets/{year_month} (t14 ac3)."""

    def test_get_stored_budget_returns_200_with_the_two_frozen_keys(
        self, tmp_path: Path
    ) -> None:
        """GET of a stored own budget echoes the two-key body."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        assert _put(client, token, "2026-10", "2000.00").status_code == 200

        response = client.get("/api/v1/budgets/2026-10", headers=_auth(token))

        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == BUDGET_FIELDS
        assert body["year_month"] == "2026-10"
        assert body["amount"] == "2000.00"
        assert isinstance(body["amount"], str) and TWO_DP.match(body["amount"])

    def test_get_absent_month_returns_200_exact_zero_body_and_persists_nothing(
        self, tmp_path: Path
    ) -> None:
        """Absence is 200 with the EXACT zero body, never 404 (REQ-API-050)."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        response = client.get("/api/v1/budgets/2026-10", headers=_auth(token))

        assert response.status_code == 200
        assert response.status_code != 404
        body = cast("dict[str, Any]", response.json())
        assert body == {"year_month": "2026-10", "amount": "0.00"}
        assert '"amount":"0.00"' in response.text.replace(" ", ""), response.text
        assert TWO_DP.match(cast("str", body["amount"]))
        assert _budget_count(override) == 0  # the GET persists NOTHING

    def test_other_users_budget_is_never_returned(self, tmp_path: Path) -> None:
        """Two real users: the caller reads "0.00", the owner reads the amount."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        assert _put(client, bob, "2026-10", "1500.00").status_code == 200

        as_alice = client.get("/api/v1/budgets/2026-10", headers=_auth(alice))
        as_bob = client.get("/api/v1/budgets/2026-10", headers=_auth(bob))

        assert as_alice.status_code == 200  # GET has NO cross-user 404 state
        assert as_alice.json() == {"year_month": "2026-10", "amount": "0.00"}
        assert as_bob.status_code == 200
        assert as_bob.json()["amount"] == "1500.00"
        # the owner's row is untouched and belongs to bob only
        assert _budget_rows(override) == [("2026-10", Decimal("1500.00"))]

    def test_get_malformed_year_month_returns_422_never_404_never_zero_body(
        self, tmp_path: Path
    ) -> None:
        """W8 FROZEN on GET: malformed forms are 422, never 404/"0.00"."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        for month in MALFORMED_MONTHS:
            response = client.get(f"/api/v1/budgets/{month}", headers=_auth(token))

            assert response.status_code == 422, month
            assert response.status_code != 404, month
            body = cast("dict[str, Any]", response.json())
            assert body["code"] == "VALIDATION_ERROR", month
            assert body["field"] == "year_month", month
            assert body.get("amount") != "0.00", month  # never the zero body
        assert _budget_count(override) == 0

    def test_get_without_token_returns_401(self, tmp_path: Path) -> None:
        """Unauthenticated GET is 401 (REQ-SEC-022)."""
        client, override = _make_client(tmp_path)
        _seed(override)

        response = client.get("/api/v1/budgets/2026-10")

        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert body["code"] == "UNAUTHORIZED"


class TestBudgetDelete:
    """Contract coverage for DELETE /api/v1/budgets/{year_month} (t14 ac4)."""

    def test_delete_own_returns_204_and_the_row_is_gone(self, tmp_path: Path) -> None:
        """204 with an empty body; a fresh session confirms the row is gone."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        assert _put(client, token, "2026-10", "2000.00").status_code == 200

        response = client.delete("/api/v1/budgets/2026-10", headers=_auth(token))

        assert response.status_code == 204
        assert response.content == b""
        assert _budget_count(override) == 0

    def test_delete_absent_and_other_user_return_identical_404_and_the_row_survives(
        self, tmp_path: Path
    ) -> None:
        """Absent and cross-user DELETEs are identical 404s; victim keeps row."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        assert _put(client, bob, "2026-10", "1500.00").status_code == 200

        absent = client.delete("/api/v1/budgets/2026-01", headers=_auth(alice))
        cross = client.delete("/api/v1/budgets/2026-10", headers=_auth(alice))

        assert absent.status_code == 404 and cross.status_code == 404
        assert absent.status_code != 403 and cross.status_code != 403
        assert absent.json() == cross.json()  # IDENTICAL bodies
        for response in (absent, cross):
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS
            assert body["code"] == "NOT_FOUND"
            assert body["field"] is None
        # the victim's budget SURVIVES
        assert _budget_rows(override) == [("2026-10", Decimal("1500.00"))]

    def test_delete_malformed_year_month_returns_422(self, tmp_path: Path) -> None:
        """W8 FROZEN on DELETE: malformed forms are 422, never 404."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        for month in MALFORMED_MONTHS:
            response = client.delete(f"/api/v1/budgets/{month}", headers=_auth(token))

            assert response.status_code == 422, month
            assert response.status_code != 404, month
            body = cast("dict[str, Any]", response.json())
            assert body["code"] == "VALIDATION_ERROR", month
            assert body["field"] == "year_month", month

    def test_deleting_budget_leaves_same_month_expenses_intact_and_queryable(
        self, tmp_path: Path
    ) -> None:
        """REQ-DB-042: budget DELETE never touches the month's expenses."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        with next(override()) as session:
            groceries_id = session.scalars(
                select(Category.id).where(
                    Category.name == "Groceries", Category.is_system.is_(True)
                )
            ).one()
        created = client.post(
            "/api/v1/expenses",
            json={
                "amount": "42.42",
                "category_id": str(groceries_id),
                "date": "2026-10-05",
                "note": "same month",
            },
            headers=_auth(token),
        )
        assert created.status_code == 201
        expense_id = cast("dict[str, Any]", created.json())["id"]
        assert _put(client, token, "2026-10", "2000.00").status_code == 200

        response = client.delete("/api/v1/budgets/2026-10", headers=_auth(token))

        assert response.status_code == 204
        # fresh session: the expense row still exists with its amount
        with next(override()) as session:
            expense = session.scalars(
                select(Expense).where(Expense.id == uuid.UUID(expense_id))
            ).one()
            assert expense.amount.quantize(Decimal("0.01")) == Decimal("42.42")
        # and the expenses list endpoint still returns it
        listing = cast(
            "dict[str, Any]",
            client.get("/api/v1/expenses?year_month=2026-10", headers=_auth(token)).json(),
        )
        assert [item["id"] for item in listing["items"]] == [expense_id]
        assert listing["items"][0]["amount"] == "42.42"


class TestBudgetOpenApi:
    """OpenAPI surface (t14 ac6)."""

    def test_openapi_lists_three_budget_operations_after_health_auth_categories_expenses(
        self, tmp_path: Path
    ) -> None:
        """Three budget operations, registered after the earlier routers."""
        client, override = _make_client(tmp_path)
        _seed(override)

        schema = cast("dict[str, Any]", client.get("/openapi.json").json())
        paths = cast("dict[str, Any]", schema["paths"])
        keys = list(paths.keys())

        assert set(paths["/api/v1/budgets/{year_month}"].keys()) == {
            "get",
            "put",
            "delete",
        }
        for earlier in (
            "/api/v1/health",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/me",
            "/api/v1/categories",
            "/api/v1/categories/{category_id}",
            "/api/v1/expenses",
            "/api/v1/expenses/{expense_id}",
        ):
            assert earlier in paths
            assert keys.index(earlier) < keys.index("/api/v1/budgets/{year_month}")
        assert not [key for key in keys if "audit" in key]
