"""Integration tests for /api/v1/dashboard (t19 ac1..ac4, ac6).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs (46-node
frozen inventory, docs/issues/t19.md).

The harness is a COPY of the merged t13/t14 pattern from
tests/integration/test_expense_api.py and test_budget_api.py (there is
no tests/conftest.py and no cross-test-module imports). Isolation
follows the groom pin: one private SQLite file PER TEST under
``tmp_path``, schema via ``Base.metadata.create_all`` (NOT alembic),
app isolation through ``dependency_overrides[get_db]``, the ten system
categories provisioned through the merged seed, and cross-user cases
registering TWO real users through the real register endpoint.

Wire-behavior pins exercised here (docs/issues/t19.md):

* Every endpoint answers the frozen 401 ``{detail, code, field: null}``
  without a token (merged ``get_current_user``).
* Money fields are 2-dp strings over the wire; ``percentage`` is a
  JSON number or ``null`` (issue ruling 1).
* Missing/malformed ``year_month`` and out-of-range/non-integer
  ``months`` / ``weeks`` / ``limit`` all render the merged 422
  ``{detail, code: VALIDATION_ERROR, field}`` shape.
* ``recent`` items reuse the merged ten-key expense wire shape.
* The OpenAPI node pins the six new GET-only paths registered AFTER
  ``/api/v1/budgets/{year_month}`` with the merged paths intact.
"""

import re
from collections.abc import Callable, Generator, Iterator
from datetime import date, timedelta
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.database import create_db_engine, create_session_factory, get_db
from app.main import create_app
from app.models import Base
from app.models.category import Category
from app.scripts.seed import seed_system_categories

SUMMARY_KEYS = {
    "year_month",
    "total",
    "budget_amount",
    "remaining",
    "percentage",
    "is_over_budget",
    "category_count",
}
BY_CATEGORY_KEYS = {"year_month", "total", "categories"}
CATEGORY_ROW_KEYS = {"category_id", "category_name", "color", "amount", "percentage"}
# The MERGED ten-key expense wire shape (issue ac4 pin; the merged
# schemas/expense.py names currency/category fields date/created_at/
# updated_at -- is_edited/replaced_expense_id arrive with t21's schema).
EXPENSE_KEYS = {
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
DAY_KEYS = {"date", "daily", "cumulative"}
ERROR_KEYS = {"detail", "code", "field"}
TWO_DP = re.compile(r"^-?[0-9]+\.[0-9]{2}$")
MALFORMED_MONTHS = ("2026-1", "2026-13", "2026-1-01", "abcd-ef")
TEST_SECRET = "dashboard-integration-secret-not-a-real-key"

DASHBOARD_PATHS = (
    "/api/v1/dashboard/summary",
    "/api/v1/dashboard/by-category",
    "/api/v1/dashboard/trend",
    "/api/v1/dashboard/cumulative",
    "/api/v1/dashboard/heatmap",
    "/api/v1/dashboard/recent",
)
MERGED_PATHS = (
    "/api/v1/categories",
    "/api/v1/expenses",
    "/api/v1/expenses/{expense_id}",
    "/api/v1/budgets/{year_month}",
)


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
        override generator function itself.
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't19_test.db').as_posix()}")
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


def _category_id(override: Callable[[], Generator[Session, None, None]], name: str) -> str:
    """Return the id string of a seeded system category.

    Args:
        override: The ``get_db`` override generator function.
        name: System category name.

    Returns:
        str: Canonical UUID string of that row.
    """
    from sqlalchemy import select

    with next(override()) as session:
        row = session.scalars(
            select(Category.id).where(Category.name == name, Category.is_system.is_(True))
        ).one()
    return str(row)


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


def _create_expense(
    client: TestClient, token: str, category_id: str, day: date, amount: str
) -> None:
    """Create one expense through the real POST endpoint.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        category_id: System category id string.
        day: Expense calendar date.
        amount: 2-dp amount string.
    """
    response = client.post(
        "/api/v1/expenses",
        json={"amount": amount, "category_id": category_id, "date": day.isoformat()},
        headers=_auth(token),
    )
    assert response.status_code == 201


def _put_budget(client: TestClient, token: str, month: str, amount: str) -> None:
    """Set one budget through the real PUT endpoint.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        month: ``YYYY-MM`` path value.
        amount: 2-dp amount string.
    """
    response = client.put(
        f"/api/v1/budgets/{month}", json={"amount": amount}, headers=_auth(token)
    )
    assert response.status_code == 200


def _setup(tmp_path: Path, name: str) -> tuple[TestClient, str, dict[str, str]]:
    """Bring up client + seeded categories + one registered user.

    Args:
        tmp_path: pytest-provided directory.
        name: Unused discriminator kept for readability of call sites.

    Returns:
        tuple: The client, the caller's token, and the system-category
        id map keyed by category name.
    """
    del name  # single per-test database; name kept for call-site clarity
    client, override = _make_client(tmp_path)
    _seed(override)
    cats = {
        "Food": _category_id(override, "Food & Dining"),
        "Transport": _category_id(override, "Transportation"),
        "Housing & Rent": _category_id(override, "Housing & Rent"),
    }
    _register(client, "alice@example.com", "alice")
    token = _login(client, "alice@example.com")
    return client, token, cats


def _current_month() -> date:
    """Return today's date (trend/heatmap defaults anchor on the clock).

    Returns:
        date: The current date.
    """
    return date.today()


class TestDashboardSummaryApi:
    """GET /api/v1/dashboard/summary wire contract (t19 ac1/ac2)."""

    def test_summary_without_token_returns_401_with_the_frozen_error_shape(
        self, tmp_path: Path
    ) -> None:
        """No token: 401 with EXACTLY {detail, code, field: null}."""
        client, _ = _make_client(tmp_path)
        response = client.get("/api/v1/dashboard/summary?year_month=2026-02")
        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_KEYS
        assert body["field"] is None
        assert isinstance(body["detail"], str)
        assert isinstance(body["code"], str)

    def test_summary_empty_month_returns_the_seven_frozen_keys_with_zero_strings(
        self, tmp_path: Path
    ) -> None:
        """Empty month: 7 frozen keys, "0.00" strings, null percentage."""
        client, token, _ = _setup(tmp_path, "empty")
        response = client.get("/api/v1/dashboard/summary?year_month=2026-02", headers=_auth(token))
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == SUMMARY_KEYS
        assert body["year_month"] == "2026-02"
        assert body["total"] == "0.00"
        assert body["budget_amount"] == "0.00"
        assert body["remaining"] == "0.00"
        assert body["percentage"] is None
        assert body["is_over_budget"] is False
        assert body["category_count"] == 0

    def test_summary_with_budget_and_expenses_returns_string_money(
        self, tmp_path: Path
    ) -> None:
        """Seeded budget+expenses: 2-dp string money, 62.5 number online."""
        client, token, cats = _setup(tmp_path, "seeded")
        _put_budget(client, token, "2026-02", "400.00")
        _create_expense(client, token, cats["Food"], date(2026, 2, 10), "150.00")
        _create_expense(client, token, cats["Transport"], date(2026, 2, 20), "100.00")
        response = client.get("/api/v1/dashboard/summary?year_month=2026-02", headers=_auth(token))
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == SUMMARY_KEYS
        assert body["total"] == "250.00"
        assert body["budget_amount"] == "400.00"
        assert body["remaining"] == "150.00"
        assert TWO_DP.match(body["total"])
        assert body["percentage"] == 62.5
        assert isinstance(body["percentage"], float)
        assert body["is_over_budget"] is False
        assert body["category_count"] == 2

    def test_summary_missing_year_month_and_malformed_forms_return_422(
        self, tmp_path: Path
    ) -> None:
        """Missing + all four malformed forms: 422 VALIDATION_ERROR."""
        client, token, _ = _setup(tmp_path, "422")
        response = client.get("/api/v1/dashboard/summary", headers=_auth(token))
        assert response.status_code == 422
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_KEYS
        assert body["code"] == "VALIDATION_ERROR"
        for malformed in MALFORMED_MONTHS:
            bad = client.get(
                f"/api/v1/dashboard/summary?year_month={malformed}", headers=_auth(token)
            )
            assert bad.status_code == 422, malformed
            assert cast("dict[str, Any]", bad.json())["code"] == "VALIDATION_ERROR", malformed

    def test_summary_never_returns_another_users_expenses_or_budget(
        self, tmp_path: Path
    ) -> None:
        """Bob's seeded data leaves Alice's summary at the empty body."""
        client, override = _make_client(tmp_path)
        _seed(override)
        food = _category_id(override, "Food & Dining")
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        _put_budget(client, bob, "2026-02", "999.00")
        _create_expense(client, bob, food, date(2026, 2, 10), "500.00")

        response = client.get("/api/v1/dashboard/summary?year_month=2026-02", headers=_auth(alice))
        body = cast("dict[str, Any]", response.json())
        assert body["total"] == "0.00"
        assert body["budget_amount"] == "0.00"
        assert body["category_count"] == 0


class TestDashboardByCategoryApi:
    """GET /api/v1/dashboard/by-category wire contract (t19 ac1/ac2)."""

    def test_by_category_without_token_returns_401_with_the_frozen_error_shape(
        self, tmp_path: Path
    ) -> None:
        """No token: 401 with EXACTLY {detail, code, field: null}."""
        client, _ = _make_client(tmp_path)
        response = client.get("/api/v1/dashboard/by-category?year_month=2026-02")
        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_KEYS
        assert body["field"] is None

    def test_by_category_empty_month_returns_the_three_frozen_keys(
        self, tmp_path: Path
    ) -> None:
        """Empty month: exactly 3 keys, total "0.00", categories []."""
        client, token, _ = _setup(tmp_path, "empty")
        response = client.get(
            "/api/v1/dashboard/by-category?year_month=2026-02", headers=_auth(token)
        )
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == BY_CATEGORY_KEYS
        assert body["year_month"] == "2026-02"
        assert body["total"] == "0.00"
        assert body["categories"] == []

    def test_by_category_rows_carry_the_five_frozen_keys_and_string_amounts(
        self, tmp_path: Path
    ) -> None:
        """Seeded rows: 5 frozen keys each, 2-dp string amounts, desc."""
        client, token, cats = _setup(tmp_path, "rows")
        _create_expense(client, token, cats["Food"], date(2026, 2, 10), "30.00")
        _create_expense(client, token, cats["Transport"], date(2026, 2, 11), "70.00")
        response = client.get(
            "/api/v1/dashboard/by-category?year_month=2026-02", headers=_auth(token)
        )
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        rows = cast("list[dict[str, Any]]", body["categories"])
        assert len(rows) == 2
        for row in rows:
            assert set(row.keys()) == CATEGORY_ROW_KEYS
            assert TWO_DP.match(row["amount"]), row["amount"]
        assert [row["amount"] for row in rows] == ["70.00", "30.00"]
        assert body["total"] == "100.00"


class TestDashboardTrendApi:
    """GET /api/v1/dashboard/trend wire contract (t19 ac1/ac3)."""

    def test_trend_without_token_returns_401_with_the_frozen_error_shape(
        self, tmp_path: Path
    ) -> None:
        """No token: 401 with EXACTLY {detail, code, field: null}."""
        client, _ = _make_client(tmp_path)
        response = client.get("/api/v1/dashboard/trend")
        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_KEYS
        assert body["field"] is None

    def test_trend_default_without_param_returns_six_month_rows(self, tmp_path: Path) -> None:
        """No params: 6 contiguous ascending months ending this month."""
        client, token, _ = _setup(tmp_path, "default")
        response = client.get("/api/v1/dashboard/trend", headers=_auth(token))
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        months = cast("list[dict[str, Any]]", body["months"])
        assert len(months) == 6
        today = _current_month()
        expected: list[str] = []
        year, month = today.year, today.month
        for _ in range(6):
            expected.append(f"{year:04d}-{month:02d}")
            month -= 1
            if month == 0:
                year, month = year - 1, 12
        assert [item["year_month"] for item in months] == list(reversed(expected))
        for item in months:
            assert set(item.keys()) == {"year_month", "total"}
            assert TWO_DP.match(item["total"])

    def test_trend_months_out_of_range_or_non_integer_return_422(self, tmp_path: Path) -> None:
        """months in {0, 25, 1.5, abc}: 422 VALIDATION_ERROR each."""
        client, token, _ = _setup(tmp_path, "months422")
        for bad in ("0", "25", "1.5", "abc"):
            response = client.get(f"/api/v1/dashboard/trend?months={bad}", headers=_auth(token))
            assert response.status_code == 422, bad
            assert cast("dict[str, Any]", response.json())["code"] == "VALIDATION_ERROR", bad


class TestDashboardCumulativeApi:
    """GET /api/v1/dashboard/cumulative wire contract (t19 ac1/ac4)."""

    def test_cumulative_without_token_returns_401_with_the_frozen_error_shape(
        self, tmp_path: Path
    ) -> None:
        """No token: 401 with EXACTLY {detail, code, field: null}."""
        client, _ = _make_client(tmp_path)
        response = client.get("/api/v1/dashboard/cumulative?year_month=2026-03")
        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_KEYS
        assert body["field"] is None

    def test_cumulative_returns_every_day_of_the_month_with_string_money(
        self, tmp_path: Path
    ) -> None:
        """March with 2 expenses: 31 rows, {date,daily,cumulative} keys."""
        client, token, cats = _setup(tmp_path, "days")
        _create_expense(client, token, cats["Food"], date(2026, 3, 5), "10.00")
        _create_expense(client, token, cats["Transport"], date(2026, 3, 31), "2.50")
        response = client.get(
            "/api/v1/dashboard/cumulative?year_month=2026-03", headers=_auth(token)
        )
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        days = cast("list[dict[str, Any]]", body["days"])
        assert len(days) == 31
        assert days[0]["date"] == "2026-03-01"
        assert days[-1]["date"] == "2026-03-31"
        for day in days:
            assert set(day.keys()) == DAY_KEYS
            assert TWO_DP.match(day["daily"]), day["daily"]
            assert TWO_DP.match(day["cumulative"]), day["cumulative"]
        running = "0.00"
        total = 0.0
        for day in days:
            total += float(day["daily"])
            running = day["cumulative"]
        assert running == f"{total:.2f}"
        assert running == "12.50"


class TestDashboardHeatmapApi:
    """GET /api/v1/dashboard/heatmap wire contract (t19 ac1/ac4)."""

    def test_heatmap_without_token_returns_401_with_the_frozen_error_shape(
        self, tmp_path: Path
    ) -> None:
        """No token: 401 with EXACTLY {detail, code, field: null}."""
        client, _ = _make_client(tmp_path)
        response = client.get("/api/v1/dashboard/heatmap")
        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_KEYS
        assert body["field"] is None

    def test_heatmap_default_returns_twelve_seven_day_week_rows(self, tmp_path: Path) -> None:
        """No params: 12 Monday-aligned rows x 7 days ending this Sunday."""
        client, token, _ = _setup(tmp_path, "default")
        response = client.get("/api/v1/dashboard/heatmap", headers=_auth(token))
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == {"max_amount", "weeks"}
        weeks = cast("list[dict[str, Any]]", body["weeks"])
        assert len(weeks) == 12
        for week in weeks:
            assert set(week.keys()) == {"week_start", "days"}
            assert len(week["days"]) == 7
            start = date.fromisoformat(week["week_start"])
            assert start.weekday() == 0  # Monday-aligned
        last = weeks[-1]["days"][-1]["date"]
        today = _current_month()
        expected_end = today + timedelta(days=6 - today.weekday())
        assert last == expected_end.isoformat()

    def test_heatmap_weeks_out_of_range_or_non_integer_return_422(self, tmp_path: Path) -> None:
        """weeks in {0, 53, 1.5}: 422 VALIDATION_ERROR each."""
        client, token, _ = _setup(tmp_path, "weeks422")
        for bad in ("0", "53", "1.5"):
            response = client.get(f"/api/v1/dashboard/heatmap?weeks={bad}", headers=_auth(token))
            assert response.status_code == 422, bad
            assert cast("dict[str, Any]", response.json())["code"] == "VALIDATION_ERROR", bad


class TestDashboardRecentApi:
    """GET /api/v1/dashboard/recent wire contract (t19 ac1/ac4)."""

    def test_recent_without_token_returns_401_with_the_frozen_error_shape(
        self, tmp_path: Path
    ) -> None:
        """No token: 401 with EXACTLY {detail, code, field: null}."""
        client, _ = _make_client(tmp_path)
        response = client.get("/api/v1/dashboard/recent")
        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_KEYS
        assert body["field"] is None

    def test_recent_default_returns_ten_items_in_the_frozen_expense_shape(
        self, tmp_path: Path
    ) -> None:
        """12 expenses exist: default returns 10 in the merged 10-key shape."""
        client, token, cats = _setup(tmp_path, "recent10")
        for day in range(1, 13):
            _create_expense(client, token, cats["Food"], date(2026, 2, day), "1.00")
        response = client.get("/api/v1/dashboard/recent", headers=_auth(token))
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == {"items"}
        items = cast("list[dict[str, Any]]", body["items"])
        assert len(items) == 10
        for item in items:
            assert set(item.keys()) == EXPENSE_KEYS
            assert TWO_DP.match(item["amount"]), item["amount"]

    def test_recent_limit_caps_items_and_out_of_range_limits_return_422(
        self, tmp_path: Path
    ) -> None:
        """limit=50 is accepted; {0, 51, 1.5} are 422 VALIDATION_ERROR."""
        client, token, cats = _setup(tmp_path, "limit422")
        for day in range(1, 13):
            _create_expense(client, token, cats["Food"], date(2026, 2, day), "1.00")
        ok = client.get("/api/v1/dashboard/recent?limit=50", headers=_auth(token))
        assert ok.status_code == 200
        assert len(cast("list[dict[str, Any]]", cast("dict[str, Any]", ok.json())["items"])) == 12
        for bad in ("0", "51", "1.5"):
            response = client.get(f"/api/v1/dashboard/recent?limit={bad}", headers=_auth(token))
            assert response.status_code == 422, bad
            assert cast("dict[str, Any]", response.json())["code"] == "VALIDATION_ERROR", bad

    def test_recent_never_lists_another_users_expenses(self, tmp_path: Path) -> None:
        """Bob's expenses never appear in Alice's recent list."""
        client, override = _make_client(tmp_path)
        _seed(override)
        food = _category_id(override, "Food & Dining")
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        _create_expense(client, bob, food, date(2026, 2, 20), "99.00")

        response = client.get("/api/v1/dashboard/recent", headers=_auth(alice))
        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert body["items"] == []


class TestDashboardOpenApi:
    """OpenAPI registration contract (t19 ac6)."""

    def test_openapi_lists_six_get_dashboard_operations_after_the_merged_routers(
        self, tmp_path: Path
    ) -> None:
        """Six GET-only dashboard paths, after budgets, merged intact."""
        client, _ = _make_client(tmp_path)
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = cast("dict[str, Any]", response.json())
        paths = cast("dict[str, Any]", spec["paths"])
        for path in DASHBOARD_PATHS:
            assert path in paths, path
            operations = cast("dict[str, Any]", paths[path])
            assert set(operations.keys()) == {"get"}, path
        for path in MERGED_PATHS:
            assert path in paths, path
        order = list(paths.keys())
        budgets_index = order.index("/api/v1/budgets/{year_month}")
        for path in DASHBOARD_PATHS:
            assert order.index(path) > budgets_index, path
