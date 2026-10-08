"""Integration tests for /api/v1/expenses (t13 ac2..ac5, REQ-API-040..044).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

The harness is a COPY of the merged t8/t11 pattern from
tests/integration/test_auth_api.py and tests/integration/
test_categories_api.py (neither is a shared fixture library; there is no
tests/conftest.py). Isolation follows the groom pin: one private SQLite
file PER TEST under ``tmp_path``, schema via ``Base.metadata.create_all``
(NOT alembic), app isolation through ``dependency_overrides[get_db]``,
and the ten system rows provisioned through the merged seed. Cross-user
cases register TWO real users through the real register endpoint.
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
from app.models.audit_log import AuditLog
from app.models.category import Category
from app.models.expense import Expense
from app.scripts.seed import seed_system_categories

EXPENSE_FIELDS = {
    "id",
    "amount",
    "currency",
    "category_id",
    "category_name",
    "category_color",
    "date",
    "note",
    "created_at",
    "updated_at",
}
ENVELOPE_FIELDS = {"items", "total", "page", "page_size"}
ERROR_FIELDS = {"detail", "code", "field"}
TWO_DP = re.compile(r"^[0-9]+\.[0-9]{2}$")
TEST_SECRET = "expenses-integration-secret-not-a-real-key"


@pytest.fixture(autouse=True)
def _pin_jwt_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin JWT settings so tokens are issued/verified with test values.

    Teardown clears the settings cache a second time so pinned values
    cannot leak into later tests in the same process (t8 precedent).

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
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't13_test.db').as_posix()}")
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


def _register(client: TestClient, email: str, username: str) -> dict[str, Any]:
    """Register a user and return the parsed 201 body.

    Args:
        client: Isolated test client.
        email: Candidate email.
        username: Candidate username.

    Returns:
        dict[str, Any]: The register response body.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "password123"},
    )
    assert response.status_code == 201
    return cast("dict[str, Any]", response.json())


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


def _auth(token: str, ip: str | None = None) -> dict[str, str]:
    """Return bearer headers, optionally with a forwarded IP.

    Args:
        token: JWT access token.
        ip: Optional X-Forwarded-For value (multi-hop string allowed).

    Returns:
        dict[str, str]: Headers for the TestClient call.
    """
    headers = {"Authorization": f"Bearer {token}"}
    if ip is not None:
        headers["X-Forwarded-For"] = ip
    return headers


def _create(client: TestClient, token: str, payload: dict[str, Any]) -> Any:
    """POST /api/v1/expenses and return the raw response.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        payload: Create body.

    Returns:
        Any: The httpx Response object.
    """
    return client.post("/api/v1/expenses", json=payload, headers=_auth(token))


def _valid_body(cat: str, **overrides: Any) -> dict[str, Any]:
    """Build a valid create body with optional overrides.

    Args:
        cat: Category uuid string (named ``cat`` so callers may also
            override ``category_id`` / ``amount`` / ``date`` / ``note``
            through ``**overrides`` without a keyword collision).
        **overrides: Keys to add/replace/remove (None value removes).

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


def _expense_count(override: Callable[[], Generator[Session, None, None]]) -> int:
    """Count ALL expense rows through a FRESH session.

    Args:
        override: The ``get_db`` override generator function.

    Returns:
        int: Number of expense rows in the database.
    """
    with next(override()) as session:
        return int(session.scalar(select(func.count()).select_from(Expense)) or 0)


class TestExpenseCreate:
    """Contract coverage for POST /api/v1/expenses (t13 ac2)."""

    def test_create_valid_returns_201_with_exactly_the_ten_frozen_response_keys(
        self, tmp_path: Path
    ) -> None:
        """201 body is EXACTLY the ten Chapter 7 keys, no user_id leak."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")

        response = _create(client, token, _valid_body(groceries))

        assert response.status_code == 201
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == EXPENSE_FIELDS
        assert body["amount"] == "125.50"
        assert body["currency"] == "USD"
        assert body["category_id"] == groceries
        assert body["category_name"] == "Groceries"
        assert isinstance(body["category_color"], str) and body["category_color"].startswith("#")
        assert body["date"] == "2026-01-15"
        assert body["note"] == "weekly shop"
        assert isinstance(body["id"], str) and uuid.UUID(body["id"])
        assert isinstance(body["created_at"], str) and isinstance(body["updated_at"], str)
        assert "user_id" not in body

    def test_create_amount_is_a_two_dp_string_never_a_json_float(self, tmp_path: Path) -> None:
        """amount is a quoted 2-dp string in the RAW JSON, not a number."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")

        response = _create(client, token, _valid_body(groceries, amount="125.5", note=None))

        assert response.status_code == 201
        body = cast("dict[str, Any]", response.json())
        assert isinstance(body["amount"], str)
        assert TWO_DP.match(body["amount"]), body["amount"]
        assert body["amount"] == "125.50"
        assert '"amount":"125.50"' in response.text.replace(" ", ""), response.text
        assert '"amount":125.5' not in response.text.replace(" ", ""), response.text
        assert body["note"] is None

    def test_create_invalid_amount_values_return_422_invalid_amount_field_amount(
        self, tmp_path: Path
    ) -> None:
        """The five frozen amount-VALUE cases all render INVALID_AMOUNT."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")

        for bad in ("0", "-1", "1.234", "10000000000.00", ""):
            response = _create(client, token, _valid_body(groceries, amount=bad))

            assert response.status_code == 422, bad
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS, bad
            assert body["code"] == "INVALID_AMOUNT", bad
            assert body["field"] == "amount", bad
        assert _expense_count(override) == 0

    def test_create_missing_amount_missing_category_invalid_date_long_note_or_bad_currency_return_422_validation_error(  # noqa: E501 - pinned node ID
        self, tmp_path: Path
    ) -> None:
        """Structural body failures all render VALIDATION_ERROR (never INVALID_AMOUNT)."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")

        cases: list[dict[str, Any]] = [
            _valid_body(groceries, amount=None),
            _valid_body(groceries, category_id=None),
            _valid_body(groceries, date="2026-13-01"),
            _valid_body(groceries, date="not-a-date"),
            _valid_body(groceries, note="x" * 501),
            _valid_body(groceries, currency="EUR"),
        ]
        for payload in cases:
            response = _create(client, token, payload)

            assert response.status_code == 422, payload
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS, payload
            assert body["code"] == "VALIDATION_ERROR", payload
        assert _expense_count(override) == 0

    def test_create_unknown_category_returns_404_category_not_found_field_category_id(
        self, tmp_path: Path
    ) -> None:
        """A random uuid category is 404 CATEGORY_NOT_FOUND, field pinned."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        response = _create(client, token, _valid_body(str(uuid.uuid4())))

        assert response.status_code == 404
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "CATEGORY_NOT_FOUND"
        assert body["field"] == "category_id"
        assert _expense_count(override) == 0

    def test_create_with_other_users_custom_category_returns_404_and_persists_nothing(
        self, tmp_path: Path
    ) -> None:
        """Bob's custom category is 404 for Alice and stores NO row."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        private = client.post(
            "/api/v1/categories",
            json={"name": "Private", "color": "#abcdef"},
            headers=_auth(bob),
        )
        assert private.status_code == 201
        private_id = cast("dict[str, Any]", private.json())["id"]

        response = _create(client, alice, _valid_body(private_id))

        assert response.status_code == 404
        assert response.status_code != 403
        body = cast("dict[str, Any]", response.json())
        assert body["code"] == "CATEGORY_NOT_FOUND"
        assert body["field"] == "category_id"
        assert _expense_count(override) == 0


class TestExpenseList:
    """Contract coverage for GET /api/v1/expenses (t13 ac3)."""

    def test_list_envelope_has_exactly_items_total_page_page_size_with_frozen_types(
        self, tmp_path: Path
    ) -> None:
        """The W6 envelope is exactly the four Chapter 7 keys, typed."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        assert _create(client, token, _valid_body(groceries)).status_code == 201

        response = client.get("/api/v1/expenses", headers=_auth(token))

        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ENVELOPE_FIELDS
        assert isinstance(body["items"], list) and len(body["items"]) == 1
        assert isinstance(body["total"], int) and body["total"] >= 0
        assert isinstance(body["page"], int) and body["page"] >= 1
        assert isinstance(body["page_size"], int) and body["page_size"] >= 1
        assert body["page"] == 1 and body["page_size"] == 20  # frozen defaults
        assert set(body["items"][0].keys()) == EXPENSE_FIELDS

    def test_list_excludes_other_users_expenses_and_reflects_the_caller_only(
        self, tmp_path: Path
    ) -> None:
        """Two real users: each list shows only its own rows (REQ-SEC-030)."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        groceries = _system_id(override, "Groceries")
        alice_ids = set()
        for day in ("01", "02"):
            created = cast(
                "dict[str, Any]",
                _create(client, alice, _valid_body(groceries, date=f"2026-01-{day}")).json(),
            )
            alice_ids.add(created["id"])
        bob_created = cast(
            "dict[str, Any]",
            _create(client, bob, _valid_body(groceries, date="2026-01-03")).json(),
        )

        alice_body = cast(
            "dict[str, Any]", client.get("/api/v1/expenses", headers=_auth(alice)).json()
        )
        bob_body = cast(
            "dict[str, Any]", client.get("/api/v1/expenses", headers=_auth(bob)).json()
        )

        assert {item["id"] for item in alice_body["items"]} == alice_ids
        assert alice_body["total"] == 2
        assert [item["id"] for item in bob_body["items"]] == [bob_created["id"]]
        assert bob_body["total"] == 1

    def test_year_month_and_category_id_filters_combine_and_order_is_date_desc_created_at_desc(
        self, tmp_path: Path
    ) -> None:
        """Filters AND-combine; ordering is date DESC then created_at DESC."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        rent = _system_id(override, "Housing & Rent")
        # two Groceries rows in 2026-01 (different dates), one in 2026-02,
        # and one Rent row in 2026-01.
        assert _create(client, token, _valid_body(groceries, date="2026-01-10")).status_code == 201
        assert _create(client, token, _valid_body(groceries, date="2026-01-20")).status_code == 201
        assert _create(client, token, _valid_body(groceries, date="2026-02-05")).status_code == 201
        assert _create(client, token, _valid_body(rent, date="2026-01-15")).status_code == 201

        month = cast(
            "dict[str, Any]",
            client.get("/api/v1/expenses?year_month=2026-01", headers=_auth(token)).json(),
        )
        both = cast(
            "dict[str, Any]",
            client.get(
                f"/api/v1/expenses?year_month=2026-01&category_id={groceries}",
                headers=_auth(token),
            ).json(),
        )

        assert month["total"] == 3
        assert [item["date"] for item in both["items"]] == ["2026-01-20", "2026-01-10"]
        assert all(item["category_id"] == groceries for item in both["items"])
        assert both["total"] == 2  # AND-combined, not either/or
        # created_at DESC tie-break: force two same-date rows with distinct
        # created_at through a fresh session, then re-read the list.
        with next(override()) as session:
            rows = session.scalars(
                select(Expense).where(Expense.category_id == uuid.UUID(groceries))
            ).all()
            base = rows[0].created_at
            for index, row in enumerate(rows):
                row.created_at = base.replace(hour=0, minute=index)
            session.commit()
        refetched = cast(
            "dict[str, Any]",
            client.get(
                f"/api/v1/expenses?year_month=2026-01&category_id={groceries}",
                headers=_auth(token),
            ).json(),
        )
        assert [item["date"] for item in refetched["items"]] == ["2026-01-20", "2026-01-10"]
        dates = [item["date"] for item in month["items"]]
        assert dates == sorted(dates, reverse=True)  # date DESC across the page

    def test_total_counts_all_matches_while_items_is_one_page_and_second_page_differs(
        self, tmp_path: Path
    ) -> None:
        """25 rows: page_size=10 pages 1/3 are disjoint, total is 25."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        for day in range(1, 26):
            created = _create(
                client, token, _valid_body(groceries, date=f"2026-01-{day:02d}")
            )
            assert created.status_code == 201

        first = cast(
            "dict[str, Any]",
            client.get("/api/v1/expenses?page=1&page_size=10", headers=_auth(token)).json(),
        )
        third = cast(
            "dict[str, Any]",
            client.get("/api/v1/expenses?page=3&page_size=10", headers=_auth(token)).json(),
        )

        assert first["total"] == 25
        assert len(first["items"]) == 10
        assert first["page"] == 1 and first["page_size"] == 10
        assert len(third["items"]) == 5
        assert third["page"] == 3
        assert not {item["id"] for item in first["items"]} & {
            item["id"] for item in third["items"]
        }

    def test_out_of_range_page_returns_200_with_empty_items_and_full_total(
        self, tmp_path: Path
    ) -> None:
        """page=99 is 200 + empty items + full total (never 404)."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        for day in range(1, 26):
            created = _create(client, token, _valid_body(groceries, date=f"2026-01-{day:02d}"))
            assert created.status_code == 201

        response = client.get("/api/v1/expenses?page=99", headers=_auth(token))

        assert response.status_code == 200
        assert response.status_code != 404
        body = cast("dict[str, Any]", response.json())
        assert body["items"] == []
        assert body["total"] == 25
        assert body["page"] == 99

    def test_empty_filter_result_returns_200_empty_items_and_zero_total(
        self, tmp_path: Path
    ) -> None:
        """A filter matching nothing is 200 with items [] and total 0."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        assert _create(client, token, _valid_body(groceries, date="2026-01-10")).status_code == 201

        response = client.get("/api/v1/expenses?year_month=2030-06", headers=_auth(token))

        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert body["items"] == []
        assert body["total"] == 0

    def test_invalid_pagination_and_year_month_query_params_return_422_validation_error(
        self, tmp_path: Path
    ) -> None:
        """The frozen REQ-PROD-031 query cases are 422 VALIDATION_ERROR."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        for query in ("page=0", "page_size=0", "page_size=101", "year_month=2026-1"):
            response = client.get(f"/api/v1/expenses?{query}", headers=_auth(token))

            assert response.status_code == 422, query
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS, query
            assert body["code"] == "VALIDATION_ERROR", query

class TestExpenseGet:
    """Contract coverage for GET /api/v1/expenses/{id} (t13 ac3)."""

    def test_get_own_expense_returns_200_with_the_ten_frozen_keys(self, tmp_path: Path) -> None:
        """GET /{id} returns the same ten-key shape for an own row."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        created = cast(
            "dict[str, Any]", _create(client, token, _valid_body(groceries)).json()
        )

        response = client.get(f"/api/v1/expenses/{created['id']}", headers=_auth(token))

        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == EXPENSE_FIELDS
        assert body["id"] == created["id"]
        assert body["amount"] == "125.50"
        assert body["date"] == "2026-01-15"

    def test_get_unknown_and_other_user_ids_return_identical_404_not_found(
        self, tmp_path: Path
    ) -> None:
        """Unknown and cross-user GETs are byte-identical 404 NOT_FOUND."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        groceries = _system_id(override, "Groceries")
        bob_row = cast("dict[str, Any]", _create(client, bob, _valid_body(groceries)).json())

        unknown = client.get(f"/api/v1/expenses/{uuid.uuid4()}", headers=_auth(alice))
        cross = client.get(f"/api/v1/expenses/{bob_row['id']}", headers=_auth(alice))

        assert unknown.status_code == 404 and cross.status_code == 404
        assert unknown.json() == cross.json()
        for response in (unknown, cross):
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS
            assert body["code"] == "NOT_FOUND"
            assert body["field"] is None


class TestExpenseUpdate:
    """Contract coverage for PUT /api/v1/expenses/{id} (t13 ac4)."""

    def test_update_partial_body_returns_200_with_new_values(self, tmp_path: Path) -> None:
        """A one-field PUT updates that field and keeps the rest."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        rent = _system_id(override, "Housing & Rent")
        created = cast(
            "dict[str, Any]", _create(client, token, _valid_body(groceries)).json()
        )

        response = client.put(
            f"/api/v1/expenses/{created['id']}",
            json={"amount": "80.00", "category_id": rent},
            headers=_auth(token),
        )

        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == EXPENSE_FIELDS
        assert body["amount"] == "80.00"
        assert body["category_id"] == rent
        assert body["category_name"] == "Housing & Rent"
        assert body["date"] == "2026-01-15"  # untouched
        assert body["note"] == "weekly shop"  # untouched

    def test_update_with_other_users_category_returns_404_and_leaves_the_row_unchanged(
        self, tmp_path: Path
    ) -> None:
        """A foreign category_id is 404 CATEGORY_NOT_FOUND, row untouched."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        groceries = _system_id(override, "Groceries")
        alice_row = cast(
            "dict[str, Any]", _create(client, alice, _valid_body(groceries)).json()
        )
        bob_private = cast(
            "dict[str, Any]",
            client.post(
                "/api/v1/categories",
                json={"name": "Private", "color": "#abcdef"},
                headers=_auth(bob),
            ).json(),
        )

        response = client.put(
            f"/api/v1/expenses/{alice_row['id']}",
            json={"category_id": bob_private["id"]},
            headers=_auth(alice),
        )

        assert response.status_code == 404
        body = cast("dict[str, Any]", response.json())
        assert body["code"] == "CATEGORY_NOT_FOUND"
        assert body["field"] == "category_id"
        with next(override()) as session:
            row = session.scalars(
                select(Expense).where(Expense.id == uuid.UUID(alice_row["id"]))
            ).one()
            assert str(row.category_id) == groceries
            assert str(row.amount.quantize(Decimal("0.01"))) == "125.50"

    def test_update_invalid_amount_returns_422_invalid_amount(self, tmp_path: Path) -> None:
        """PUT shares the create amount rules: bad value -> INVALID_AMOUNT."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        created = cast(
            "dict[str, Any]", _create(client, token, _valid_body(groceries)).json()
        )

        response = client.put(
            f"/api/v1/expenses/{created['id']}", json={"amount": "1.234"}, headers=_auth(token)
        )

        assert response.status_code == 422
        body = cast("dict[str, Any]", response.json())
        assert body["code"] == "INVALID_AMOUNT"
        assert body["field"] == "amount"
        with next(override()) as session:
            row = session.scalars(
                select(Expense).where(Expense.id == uuid.UUID(created["id"]))
            ).one()
            assert str(row.amount.quantize(Decimal("0.01"))) == "125.50"

    def test_update_empty_body_returns_422_validation_error(self, tmp_path: Path) -> None:
        """minProperties: 1 — the empty object is 422 VALIDATION_ERROR."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        created = cast(
            "dict[str, Any]", _create(client, token, _valid_body(groceries)).json()
        )

        response = client.put(f"/api/v1/expenses/{created['id']}", json={}, headers=_auth(token))

        assert response.status_code == 422
        body = cast("dict[str, Any]", response.json())
        assert body["code"] == "VALIDATION_ERROR"

    def test_update_unknown_and_other_user_return_identical_404(self, tmp_path: Path) -> None:
        """Unknown and cross-user PUTs are byte-identical 404s; row survives."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        groceries = _system_id(override, "Groceries")
        bob_row = cast(
            "dict[str, Any]", _create(client, bob, _valid_body(groceries)).json()
        )

        unknown = client.put(
            f"/api/v1/expenses/{uuid.uuid4()}", json={"amount": "5.00"}, headers=_auth(alice)
        )
        cross = client.put(
            f"/api/v1/expenses/{bob_row['id']}", json={"amount": "5.00"}, headers=_auth(alice)
        )

        assert unknown.status_code == 404 and cross.status_code == 404
        assert unknown.json() == cross.json()
        body = cast("dict[str, Any]", unknown.json())
        assert body["code"] == "NOT_FOUND"
        assert body["field"] is None
        with next(override()) as session:
            row = session.scalars(
                select(Expense).where(Expense.id == uuid.UUID(bob_row["id"]))
            ).one()
            assert str(row.amount.quantize(Decimal("0.01"))) == "125.50"


class TestExpenseDelete:
    """Contract coverage for DELETE /api/v1/expenses/{id} (t13 ac4)."""

    def test_delete_own_returns_204_and_the_row_is_gone(self, tmp_path: Path) -> None:
        """204 with an empty body; a fresh session confirms the row is gone."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        created = cast(
            "dict[str, Any]", _create(client, token, _valid_body(groceries)).json()
        )

        response = client.delete(f"/api/v1/expenses/{created['id']}", headers=_auth(token))

        assert response.status_code == 204
        assert response.content == b""
        assert _expense_count(override) == 0

    def test_delete_unknown_and_other_user_return_identical_404_and_the_row_survives(
        self, tmp_path: Path
    ) -> None:
        """Unknown/cross-user DELETEs are identical 404s; victim keeps the row."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        groceries = _system_id(override, "Groceries")
        bob_row = cast(
            "dict[str, Any]", _create(client, bob, _valid_body(groceries)).json()
        )

        unknown = client.delete(f"/api/v1/expenses/{uuid.uuid4()}", headers=_auth(alice))
        cross = client.delete(f"/api/v1/expenses/{bob_row['id']}", headers=_auth(alice))

        assert unknown.status_code == 404 and cross.status_code == 404
        assert unknown.json() == cross.json()
        body = cast("dict[str, Any]", unknown.json())
        assert body["code"] == "NOT_FOUND"
        with next(override()) as session:
            row = session.scalars(
                select(Expense).where(Expense.id == uuid.UUID(bob_row["id"]))
            ).one()
            assert row is not None


class TestExpenseAudit:
    """API-level audit integration (t13 ac5, REQ-ARCH-078/REQ-BE-042)."""

    def test_create_update_delete_audit_rows_persist_the_forwarded_client_ip(
        self, tmp_path: Path
    ) -> None:
        """Every expense audit row carries the X-Forwarded-For first hop."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        hops = "203.0.113.7, 70.41.3.18"

        created = cast(
            "dict[str, Any]",
            client.post(
                "/api/v1/expenses",
                json=_valid_body(groceries),
                headers=_auth(token, hops),
            ).json(),
        )
        put = client.put(
            f"/api/v1/expenses/{created['id']}",
            json={"amount": "10.00"},
            headers=_auth(token, hops),
        )
        assert put.status_code == 200
        deleted = client.delete(
            f"/api/v1/expenses/{created['id']}", headers=_auth(token, hops)
        )
        assert deleted.status_code == 204

        with next(override()) as session:
            rows = session.scalars(
                select(AuditLog).where(AuditLog.entity_type == "expense")
            ).all()
            assert {row.action for row in rows} == {"CREATE", "UPDATE", "DELETE"}
            assert len(rows) == 3
            for row in rows:
                assert str(row.entity_id) == created["id"]
                assert row.ip_address == "203.0.113.7"


class TestExpenseOpenApi:
    """OpenAPI surface (t13 ac6)."""

    def test_openapi_lists_five_expense_operations_after_health_auth_categories(
        self, tmp_path: Path
    ) -> None:
        """Five expense operations, registered after the earlier routers."""
        client, override = _make_client(tmp_path)
        _seed(override)

        schema = cast("dict[str, Any]", client.get("/openapi.json").json())
        paths = cast("dict[str, Any]", schema["paths"])
        keys = list(paths.keys())

        assert set(paths["/api/v1/expenses"].keys()) == {"get", "post"}
        assert set(paths["/api/v1/expenses/{expense_id}"].keys()) == {
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
        ):
            assert earlier in paths
            assert keys.index(earlier) < keys.index("/api/v1/expenses")
        assert not [key for key in keys if "audit" in key]
