"""Money-precision and inclusive-bounds API suite (t15 ac3/ac4).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

The harness is a COPY of the merged t13/t14 pattern from
tests/integration/test_expense_api.py and tests/integration/
test_budget_api.py (there is no tests/conftest.py and no cross-test-module
imports): one private SQLite file PER TEST under ``tmp_path``, schema via
``Base.metadata.create_all``, app isolation through
``dependency_overrides[get_db]``, system rows through the merged seed, and
real register/login users.

Frozen contract (t15 groom ratification): the merged contract IS the
contract — ``AMOUNT_MAX = Decimal("999999999.99")`` with ``NUMERIC(12,2)``
columns. Amounts are 2-dp STRINGS in raw JSON (never JSON floats);
``"999999999.99"`` (AMOUNT_MAX itself) round-trips byte-exact while the
Chapter 7 ``"9999999999.99"`` over-max value is 422 INVALID_AMOUNT field
``amount`` with nothing persisted. The bounds matrix (ac4) pins the ACCEPT
side at the exact merged limits only.
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
from app.services.expense_service import parse_amount

ENVELOPE_FIELDS = {"items", "total", "page", "page_size"}
ERROR_FIELDS = {"detail", "code", "field"}
TWO_DP = re.compile(r"^[0-9]+\.[0-9]{2}$")
TEST_SECRET = "money-integration-secret-not-a-real-key"


@pytest.fixture(autouse=True)
def _pin_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin JWT settings so tokens are issued/verified with test values.

    Teardown clears the settings cache a second time so pinned values
    cannot leak into later tests in the same process (t8/t13/t14
    precedent).

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
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't15_money.db').as_posix()}")
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


def _system_id(override: Callable[[], Generator[Session, None, None]], name: str) -> str:
    """Return the id string of a seeded system category.

    Args:
        override: The ``get_db`` override generator function.
        name: System category name.

    Returns:
        str: Canonical UUID string of that row.
    """
    with next(override()) as session:
        row = session.scalars(
            select(Category.id).where(Category.name == name, Category.is_system.is_(True))
        ).one()
    return str(row)


def _register(
    client: TestClient, email: str, username: str, password: str = "password123"
) -> dict[str, Any]:
    """Register a user and return the parsed response.

    Args:
        client: Isolated test client.
        email: Candidate email.
        username: Candidate username.
        password: Candidate password.

    Returns:
        dict[str, Any]: The raw register response body.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert response.status_code == 201
    return cast("dict[str, Any]", response.json())


def _login(client: TestClient, email: str, password: str = "password123") -> str:
    """Log in through the real login endpoint.

    Args:
        client: Isolated test client.
        email: Account email.
        password: Account password.

    Returns:
        str: The JWT access token.
    """
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
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


def _valid_body(cat: str, **overrides: Any) -> dict[str, Any]:
    """Build a valid expense-create body with optional overrides.

    Args:
        cat: Category uuid string.
        **overrides: Keys to add/replace (None value removes).

    Returns:
        dict[str, Any]: The request body.
    """
    body: dict[str, Any] = {
        "amount": "125.50",
        "category_id": cat,
        "date": "2026-01-15",
        "note": "weekly shop",
    }
    for key, value in overrides.items():
        if value is None and key in body:
            del body[key]
        else:
            body[key] = value
    return body


def _create_raw(client: TestClient, token: str, payload: dict[str, Any]) -> Any:
    """POST /api/v1/expenses and return the raw response.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        payload: Create body.

    Returns:
        Any: The httpx Response object.
    """
    return client.post("/api/v1/expenses", json=payload, headers=_auth(token))


def _create(client: TestClient, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST /api/v1/expenses asserting 201, returning the body.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        payload: Create body.

    Returns:
        dict[str, Any]: The created expense body.
    """
    response = _create_raw(client, token, payload)
    assert response.status_code == 201
    return cast("dict[str, Any]", response.json())


def _assert_amount_string(response: Any, expected: str) -> None:
    """Assert the RAW JSON carries ``expected`` as a quoted 2-dp string.

    Args:
        response: A response carrying an expense ``amount``.
        expected: The pinned 2-dp string, e.g. ``"0.10"``.

    Raises:
        AssertionError: When the raw text or the parsed value deviates.
    """
    raw = response.text.replace(" ", "")
    assert f'"amount":"{expected}"' in raw, response.text
    assert f'"amount":{expected}' not in raw, response.text  # never a JSON float
    body = cast("dict[str, Any]", response.json())
    assert isinstance(body["amount"], str)
    assert body["amount"] == expected
    assert TWO_DP.match(body["amount"]), body["amount"]


def _expense_count(override: Callable[[], Generator[Session, None, None]]) -> int:
    """Count ALL expense rows through a FRESH session.

    Args:
        override: The ``get_db`` override generator function.

    Returns:
        int: Number of expense rows in the database.
    """
    with next(override()) as session:
        return int(session.scalar(select(func.count()).select_from(Expense)) or 0)


def _budget_amount(
    override: Callable[[], Generator[Session, None, None]], month: str
) -> Decimal:
    """Return the single persisted amount for one month, fresh.

    Args:
        override: The ``get_db`` override generator function.
        month: year_month key.

    Returns:
        Decimal: The stored amount quantized to 2 dp.
    """
    with next(override()) as session:
        row = session.scalars(select(Budget).where(Budget.year_month == month)).one()
    return row.amount.quantize(Decimal("0.01"))


class TestMoneyPrecisionRoundTrip:
    """Full HTTP -> DB -> HTTP 2-dp string round-trips (ac3)."""

    def test_expense_amount_round_trips_byte_exact_through_create_get_put_and_list(
        self, tmp_path: Path
    ) -> None:  # noqa: E501 - pinned node ID
        """"0.10" -> PUT "0.01" stays an exact 2-dp string on every seam."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")

        created = _create_raw(client, token, _valid_body(groceries, amount="0.10", note=None))
        assert created.status_code == 201
        _assert_amount_string(created, "0.10")
        expense_id = cast("dict[str, Any]", created.json())["id"]

        fetched = client.get(f"/api/v1/expenses/{expense_id}", headers=_auth(token))
        assert fetched.status_code == 200
        _assert_amount_string(fetched, "0.10")

        listed = client.get("/api/v1/expenses", headers=_auth(token))
        assert listed.status_code == 200
        list_body = cast("dict[str, Any]", listed.json())
        assert set(list_body.keys()) == ENVELOPE_FIELDS
        assert [item["amount"] for item in list_body["items"]] == ["0.10"]
        assert '"amount":"0.10"' in listed.text.replace(" ", ""), listed.text

        updated = client.put(
            f"/api/v1/expenses/{expense_id}", json={"amount": "0.01"}, headers=_auth(token)
        )
        assert updated.status_code == 200
        _assert_amount_string(updated, "0.01")

        refetched = client.get(f"/api/v1/expenses/{expense_id}", headers=_auth(token))
        _assert_amount_string(refetched, "0.01")
        relisted = client.get("/api/v1/expenses", headers=_auth(token))
        assert [item["amount"] for item in cast(
            "dict[str, Any]", relisted.json()
        )["items"]] == ["0.01"]
        with next(override()) as session:
            row = session.scalars(
                select(Expense).where(Expense.id == uuid.UUID(expense_id))
            ).one()
            assert str(row.amount.quantize(Decimal("0.01"))) == "0.01"

    def test_maximum_amount_round_trips_and_the_chapter_over_max_value_is_rejected_422_invalid_amount(  # noqa: E501 - pinned node ID
        self, tmp_path: Path
    ) -> None:
        """AMOUNT_MAX round-trips byte-exact; 9999999999.99 is 422, stored nothing."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")

        created = _create_raw(client, token, _valid_body(groceries, amount="999999999.99"))
        assert created.status_code == 201
        _assert_amount_string(created, "999999999.99")
        expense_id = cast("dict[str, Any]", created.json())["id"]

        fetched = client.get(f"/api/v1/expenses/{expense_id}", headers=_auth(token))
        _assert_amount_string(fetched, "999999999.99")
        listed = client.get("/api/v1/expenses", headers=_auth(token))
        assert [item["amount"] for item in cast(
            "dict[str, Any]", listed.json()
        )["items"]] == ["999999999.99"]
        updated = client.put(
            f"/api/v1/expenses/{expense_id}",
            json={"amount": "999999999.99"},
            headers=_auth(token),
        )
        assert updated.status_code == 200
        _assert_amount_string(updated, "999999999.99")
        with next(override()) as session:
            row = session.scalars(
                select(Expense).where(Expense.id == uuid.UUID(expense_id))
            ).one()
            assert str(row.amount.quantize(Decimal("0.01"))) == "999999999.99"

        # Chapter 7 7.10.1's over-max value: 422 INVALID_AMOUNT, nothing new.
        over = _create_raw(client, token, _valid_body(groceries, amount="9999999999.99"))
        assert over.status_code == 422
        body = cast("dict[str, Any]", over.json())
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "INVALID_AMOUNT"
        assert body["field"] == "amount"
        assert _expense_count(override) == 1  # only the round-trip row exists

    def test_budget_amount_round_trips_byte_exact_through_put_get_and_delete(
        self, tmp_path: Path
    ) -> None:
        """Budget "1234.56" survives PUT -> GET -> list-free DELETE as a string."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        put = client.put(
            "/api/v1/budgets/2026-08", json={"amount": "1234.56"}, headers=_auth(token)
        )
        assert put.status_code == 200
        _assert_amount_string(put, "1234.56")
        assert cast("dict[str, Any]", put.json())["year_month"] == "2026-08"

        fetched = client.get("/api/v1/budgets/2026-08", headers=_auth(token))
        assert fetched.status_code == 200
        _assert_amount_string(fetched, "1234.56")
        assert _budget_amount(override, "2026-08") == Decimal("1234.56")

        deleted = client.delete("/api/v1/budgets/2026-08", headers=_auth(token))
        assert deleted.status_code == 204
        after = client.get("/api/v1/budgets/2026-08", headers=_auth(token))
        assert after.status_code == 200
        assert after.json() == {"year_month": "2026-08", "amount": "0.00"}


class TestDecimalAggregation:
    """Service-level Decimal seam stays float-free (ac3)."""

    def test_service_decimal_amounts_sum_without_float_artifacts(self) -> None:
        """parse_amount is str-in/Decimal-out; sums carry no binary-float dust."""
        values = [parse_amount(raw) for raw in ("0.10", "0.20")]
        assert all(isinstance(value, Decimal) for value in values)
        total = sum(values)
        assert isinstance(total, Decimal)
        assert total == Decimal("0.30")
        assert str(total) == "0.30"
        assert "0.30000000000000004" not in str(total)
        # The float trap the Decimal seam exists to prevent (REQ-DB-090):
        assert 0.1 + 0.2 != Decimal("0.30")


class TestBoundsMatrix:
    """W16 inclusive-bounds matrix, ACCEPT side at the exact limit (ac4)."""

    def test_amount_note_and_pagination_limits_are_inclusive(self, tmp_path: Path) -> None:
        """0.01 / 999999999.99 / 500-char note / page_size=100 are all accepted."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")

        low = _create_raw(client, token, _valid_body(groceries, amount="0.01"))
        assert low.status_code == 201
        _assert_amount_string(low, "0.01")

        high = _create_raw(client, token, _valid_body(groceries, amount="999999999.99"))
        assert high.status_code == 201
        _assert_amount_string(high, "999999999.99")

        note = "n" * 500
        noted = _create_raw(client, token, _valid_body(groceries, amount="1.00", note=note))
        assert noted.status_code == 201
        assert cast("dict[str, Any]", noted.json())["note"] == note

        paged = client.get("/api/v1/expenses?page_size=100", headers=_auth(token))
        assert paged.status_code == 200
        body = cast("dict[str, Any]", paged.json())
        assert set(body.keys()) == ENVELOPE_FIELDS
        assert body["page_size"] == 100
        assert body["total"] == 3

    def test_category_name_and_auth_field_limits_are_inclusive(self, tmp_path: Path) -> None:
        """100-char category name, 50-char username, 72-char password all pass."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        name = "c" * 100
        created = client.post(
            "/api/v1/categories",
            json={"name": name, "color": "#abcdef"},
            headers=_auth(token),
        )
        assert created.status_code == 201
        assert cast("dict[str, Any]", created.json())["name"] == name

        long_user = "u" * 50
        long_password = "p" * 72
        assert len(long_user) == 50 and len(long_password) == 72
        registered = client.post(
            "/api/v1/auth/register",
            json={
                "email": "maxfields@example.com",
                "username": long_user,
                "password": long_password,
            },
        )
        assert registered.status_code == 201
        # The account is real: login with the exact 72-char password works.
        assert (
            client.post(
                "/api/v1/auth/login",
                json={"email": "maxfields@example.com", "password": long_password},
            ).status_code
            == 200
        )
