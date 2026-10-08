"""Cross-resource user-isolation suite (t15 ac1/ac2/ac5, REQ-SEC-030..034).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

The harness is a COPY of the merged t13/t14 pattern from
tests/integration/test_expense_api.py and tests/integration/
test_budget_api.py (there is no tests/conftest.py and no cross-test-module
imports). Isolation follows the groom pin: one private SQLite file PER
TEST under ``tmp_path``, schema via ``Base.metadata.create_all`` (NOT
alembic), app isolation through ``dependency_overrides[get_db]``, and the
ten system rows provisioned through the merged seed. Every scenario
registers TWO real users through the real register/login endpoints
(Constraints: no direct DB user inserts).

Frozen contract exercised here (t15 groom pins):
cross-user GET/PUT/DELETE on expenses, budgets, and custom categories is
404 with bodies BYTE-IDENTICAL to the unknown-uuid 404 (key set exactly
{detail, code, field}, code NOT_FOUND, field None; never 403/500); a
cross-user budget GET is the 200 "0.00" absent-shape, never 404 (t14 ac3
ruling); an attacker PUT on the victim's month creates ONLY the
attacker's own row; the in-use category guard is a live 409
CATEGORY_IN_USE over HTTP that unblocks via delete-expense ->
delete-category; a SYSTEM category holding expenses is 404
CATEGORY_NOT_FOUND, never 409; and every successful expense/budget write
has exactly one audit_logs row attributed to its WRITER.
"""

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
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User
from app.scripts.seed import seed_system_categories

ENVELOPE_FIELDS = {"items", "total", "page", "page_size"}
ERROR_FIELDS = {"detail", "code", "field"}
TEST_SECRET = "isolation-integration-secret-not-a-real-key"


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
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't15_test.db').as_posix()}")
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


def _register(client: TestClient, email: str, username: str) -> str:
    """Register a user through the real register endpoint.

    Args:
        client: Isolated test client.
        email: Candidate email.
        username: Candidate username.

    Returns:
        str: The created user's canonical id string.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": "password123"},
    )
    assert response.status_code == 201
    return cast("str", cast("dict[str, Any]", response.json())["id"])


def _login(client: TestClient, email: str) -> str:
    """Log in through the real login endpoint.

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


def _create(client: TestClient, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST /api/v1/expenses asserting 201, returning the body.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        payload: Create body.

    Returns:
        dict[str, Any]: The created expense body.
    """
    response = client.post("/api/v1/expenses", json=payload, headers=_auth(token))
    assert response.status_code == 201
    return cast("dict[str, Any]", response.json())


def _create_category(client: TestClient, token: str, name: str) -> str:
    """POST /api/v1/categories asserting 201, returning the id string.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        name: Custom category name.

    Returns:
        str: The created category's id string.
    """
    response = client.post(
        "/api/v1/categories",
        json={"name": name, "color": "#abcdef"},
        headers=_auth(token),
    )
    assert response.status_code == 201
    return cast("str", cast("dict[str, Any]", response.json())["id"])


def _put_budget(client: TestClient, token: str, month: str, amount: str) -> Any:
    """PUT /api/v1/budgets/{month} and return the raw response.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        month: year_month path value.
        amount: Budget amount string.

    Returns:
        Any: The httpx Response object.
    """
    return client.put(f"/api/v1/budgets/{month}", json={"amount": amount}, headers=_auth(token))


def _assert_not_found_contract(response: Any) -> None:
    """Assert the frozen cross-user/unknown 404 contract (REQ-SEC-031).

    Args:
        response: A response expected to be the byte-pinned 404.

    Raises:
        AssertionError: When any pinned element deviates.
    """
    assert response.status_code == 404, response.text
    assert response.status_code != 403 and response.status_code != 500
    body = cast("dict[str, Any]", response.json())
    assert set(body.keys()) == ERROR_FIELDS
    assert body["code"] == "NOT_FOUND"
    assert body["field"] is None
    assert isinstance(body["detail"], str) and body["detail"]


def _expense_row(
    override: Callable[[], Generator[Session, None, None]], expense_id: str
) -> Expense | None:
    """Return the expense row through a FRESH session, or None.

    Args:
        override: The ``get_db`` override generator function.
        expense_id: Expense uuid string.

    Returns:
        Expense | None: The row, or None when absent.
    """
    with next(override()) as session:
        return session.scalars(
            select(Expense).where(Expense.id == uuid.UUID(expense_id))
        ).first()


def _budget_rows(
    override: Callable[[], Generator[Session, None, None]],
) -> list[tuple[str, str, Decimal]]:
    """Return every persisted (user_id, year_month, amount) fresh.

    Args:
        override: The ``get_db`` override generator function.

    Returns:
        list[tuple[str, str, Decimal]]: Rows quantized to 2 dp.
    """
    with next(override()) as session:
        rows = session.scalars(select(Budget).order_by(Budget.user_id, Budget.year_month)).all()
        return [
            (str(row.user_id), row.year_month, row.amount.quantize(Decimal("0.01")))
            for row in rows
        ]


class TestCrossResourceIsolation:
    """Full-chain attacker/victim matrix across all three resources (ac1)."""

    def test_full_chain_attacker_reads_updates_and_deletes_every_victim_resource(
        self, tmp_path: Path
    ) -> None:
        """Bob's every verb on Alice's rows is a contract 404; her data holds."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        groceries = _system_id(override, "Groceries")
        alice_category = _create_category(client, alice, "AlicePrivate")
        alice_expense = _create(
            client, alice, _valid_body(alice_category, amount="42.10", note="victim note")
        )
        assert _put_budget(client, alice, "2026-03", "1000.00").status_code == 200
        bob_expense = _create(client, bob, _valid_body(groceries, amount="7.00"))

        # B's list is disjoint from A's rows and reflects only B's own count.
        bob_list = client.get("/api/v1/expenses", headers=_auth(bob))
        assert bob_list.status_code == 200
        bob_body = cast("dict[str, Any]", bob_list.json())
        assert set(bob_body.keys()) == ENVELOPE_FIELDS
        assert {item["id"] for item in bob_body["items"]} == {bob_expense["id"]}
        assert alice_expense["id"] not in {item["id"] for item in bob_body["items"]}
        assert bob_body["total"] == 1

        # GET / PUT / DELETE on Alice's expense: frozen 404, never 403/500.
        cross_get = client.get(f"/api/v1/expenses/{alice_expense['id']}", headers=_auth(bob))
        cross_put = client.put(
            f"/api/v1/expenses/{alice_expense['id']}",
            json={"amount": "0.01"},
            headers=_auth(bob),
        )
        cross_delete = client.delete(f"/api/v1/expenses/{alice_expense['id']}", headers=_auth(bob))
        for response in (cross_get, cross_put, cross_delete):
            _assert_not_found_contract(response)

        # B deletes A's custom category: 404 NOT_FOUND (field None).
        cat_delete = client.delete(f"/api/v1/categories/{alice_category}", headers=_auth(bob))
        _assert_not_found_contract(cat_delete)

        # B's GET of A's budgeted month is the 200 "0.00" absent-shape.
        budget_get = client.get("/api/v1/budgets/2026-03", headers=_auth(bob))
        assert budget_get.status_code == 200
        assert budget_get.status_code != 404
        assert budget_get.json() == {"year_month": "2026-03", "amount": "0.00"}
        # ...while Alice still sees her own amount.
        own_get = client.get("/api/v1/budgets/2026-03", headers=_auth(alice))
        assert own_get.status_code == 200
        assert own_get.json() == {"year_month": "2026-03", "amount": "1000.00"}

        # B's DELETE of A's budget month: 404 NOT_FOUND, Alice's row intact.
        budget_delete = client.delete("/api/v1/budgets/2026-03", headers=_auth(bob))
        _assert_not_found_contract(budget_delete)

        # Fresh-session probes: every victim row is UNMODIFIED.
        row = _expense_row(override, alice_expense["id"])
        assert row is not None
        assert str(row.amount.quantize(Decimal("0.01"))) == "42.10"
        assert str(row.category_id) == alice_category
        assert row.note == "victim note"
        with next(override()) as session:
            category = session.get(Category, uuid.UUID(alice_category))
            assert category is not None and category.user_id is not None
        assert sorted(_budget_rows(override)) == [
            (str(_user_id(override, "alice@example.com")), "2026-03", Decimal("1000.00"))
        ]
        with next(override()) as session:
            assert int(session.scalar(select(func.count()).select_from(Expense)) or 0) == 2

    def test_cross_user_and_unknown_id_error_bodies_are_byte_identical_for_all_three_resources(
        self, tmp_path: Path
    ) -> None:  # noqa: E501 - pinned node ID
        """Unknown-uuid and cross-user 404s are byte-identical on all three."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        alice_category = _create_category(client, alice, "AlicePrivate")
        alice_expense = _create(client, alice, _valid_body(alice_category))
        assert _put_budget(client, alice, "2026-04", "777.00").status_code == 200

        pairs = [
            (
                client.get(f"/api/v1/expenses/{uuid.uuid4()}", headers=_auth(bob)),
                client.get(f"/api/v1/expenses/{alice_expense['id']}", headers=_auth(bob)),
            ),
            (
                client.put(
                    f"/api/v1/expenses/{uuid.uuid4()}",
                    json={"amount": "5.00"},
                    headers=_auth(bob),
                ),
                client.put(
                    f"/api/v1/expenses/{alice_expense['id']}",
                    json={"amount": "5.00"},
                    headers=_auth(bob),
                ),
            ),
            (
                client.delete(f"/api/v1/expenses/{uuid.uuid4()}", headers=_auth(bob)),
                client.delete(f"/api/v1/expenses/{alice_expense['id']}", headers=_auth(bob)),
            ),
            (
                client.delete(f"/api/v1/categories/{uuid.uuid4()}", headers=_auth(bob)),
                client.delete(f"/api/v1/categories/{alice_category}", headers=_auth(bob)),
            ),
            (
                client.delete("/api/v1/budgets/2030-01", headers=_auth(bob)),
                client.delete("/api/v1/budgets/2026-04", headers=_auth(bob)),
            ),
        ]
        for unknown, cross in pairs:
            _assert_not_found_contract(unknown)
            _assert_not_found_contract(cross)
            assert unknown.content == cross.content, (unknown.text, cross.text)
            assert unknown.json() == cross.json()

        # The victim's rows all survive the byte-identity probe.
        assert _expense_row(override, alice_expense["id"]) is not None
        assert sorted(_budget_rows(override)) == [
            (str(_user_id(override, "alice@example.com")), "2026-04", Decimal("777.00"))
        ]

    def test_attacker_budget_put_creates_only_the_attackers_own_row(
        self, tmp_path: Path
    ) -> None:
        """Bob PUTs Alice's month: 200 with BOB's amount, her row untouched."""
        client, override = _make_client(tmp_path)
        _seed(override)
        alice_id = _register(client, "alice@example.com", "alice")
        bob_id = _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        assert _put_budget(client, alice, "2026-05", "1000.00").status_code == 200

        attack = _put_budget(client, bob, "2026-05", "0.01")

        assert attack.status_code == 200
        assert attack.json() == {"year_month": "2026-05", "amount": "0.01"}
        # Fresh session: exactly one row per (user, month); Alice UNCHANGED.
        assert sorted(_budget_rows(override)) == sorted([
            (alice_id, "2026-05", Decimal("1000.00")),
            (bob_id, "2026-05", Decimal("0.01")),
        ])
        # Alice's own GET still returns her amount, not the attacker's.
        own_get = client.get("/api/v1/budgets/2026-05", headers=_auth(alice))
        assert own_get.status_code == 200
        assert own_get.json() == {"year_month": "2026-05", "amount": "1000.00"}


def _user_id(override: Callable[[], Generator[Session, None, None]], email: str) -> uuid.UUID:
    """Return a registered user's id through a fresh session.

    Args:
        override: The ``get_db`` override generator function.
        email: The account email.

    Returns:
        uuid.UUID: The user's id.
    """
    with next(override()) as session:
        return session.scalars(select(User.id).where(User.email == email)).one()


def _budget_id(
    override: Callable[[], Generator[Session, None, None]], user_id: str, month: str
) -> str:
    """Return the owner's budget row id for one month via a fresh session.

    Args:
        override: The ``get_db`` override generator function.
        user_id: Owner uuid string.
        month: year_month key.

    Returns:
        str: The budget row's canonical id string.
    """
    with next(override()) as session:
        row = session.scalars(
            select(Budget).where(Budget.user_id == uuid.UUID(user_id), Budget.year_month == month)
        ).one()
    return str(row.id)


class TestCategoryDeleteInUseEndToEnd:
    """API-level in-use 409, recovery, and system-ordering cases (ac2)."""

    def test_delete_category_with_a_real_expense_returns_409_and_everything_survives(
        self, tmp_path: Path
    ) -> None:
        """In-use DELETE is 409 CATEGORY_IN_USE over HTTP; both rows survive."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        alice = _login(client, "alice@example.com")
        category_id = _create_category(client, alice, "InUseCat")
        expense = _create(client, alice, _valid_body(category_id, amount="33.30"))

        response = client.delete(f"/api/v1/categories/{category_id}", headers=_auth(alice))

        assert response.status_code == 409
        assert response.status_code != 404
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "CATEGORY_IN_USE"
        assert body["field"] == "category_id"
        assert isinstance(body["detail"], str) and body["detail"]
        # Fresh session: the category AND its expense survive untouched.
        with next(override()) as session:
            assert session.get(Category, uuid.UUID(category_id)) is not None
        row = _expense_row(override, expense["id"])
        assert row is not None
        assert str(row.category_id) == category_id
        assert str(row.amount.quantize(Decimal("0.01"))) == "33.30"

    def test_delete_category_returns_204_once_its_only_expense_is_deleted(
        self, tmp_path: Path
    ) -> None:
        """Delete-expense then delete-category unblocks: 204, 204, row gone."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        alice = _login(client, "alice@example.com")
        category_id = _create_category(client, alice, "InUseCat")
        expense = _create(client, alice, _valid_body(category_id))
        assert (
            client.delete(f"/api/v1/categories/{category_id}", headers=_auth(alice)).status_code
            == 409
        )

        expense_delete = client.delete(f"/api/v1/expenses/{expense['id']}", headers=_auth(alice))
        category_delete = client.delete(f"/api/v1/categories/{category_id}", headers=_auth(alice))

        assert expense_delete.status_code == 204
        assert expense_delete.content == b""
        assert category_delete.status_code == 204
        assert category_delete.content == b""
        with next(override()) as session:
            assert session.get(Category, uuid.UUID(category_id)) is None
        assert _expense_row(override, expense["id"]) is None

    def test_delete_system_category_holding_expenses_is_404_category_not_found_never_409(
        self, tmp_path: Path
    ) -> None:  # noqa: E501 - pinned node ID
        """The system branch precedes the in-use check: 404, never 409."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        alice = _login(client, "alice@example.com")
        groceries = _system_id(override, "Groceries")
        expense = _create(client, alice, _valid_body(groceries))

        response = client.delete(f"/api/v1/categories/{groceries}", headers=_auth(alice))

        assert response.status_code == 404
        assert response.status_code != 409
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "CATEGORY_NOT_FOUND"
        assert body["field"] == "category_id"
        # The system row and the expense both survive.
        with next(override()) as session:
            assert session.get(Category, uuid.UUID(groceries)) is not None
        assert _expense_row(override, expense["id"]) is not None


class TestAuditObservabilityFromOutside:
    """Outside-in write accounting across both users (ac5)."""

    def test_every_successful_write_for_both_users_has_exactly_one_audit_row_for_its_owner(
        self, tmp_path: Path
    ) -> None:  # noqa: E501 - pinned node ID
        """Each expense/budget write has one audit row for its WRITER only."""
        client, override = _make_client(tmp_path)
        _seed(override)
        alice_id = _register(client, "alice@example.com", "alice")
        bob_id = _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        groceries = _system_id(override, "Groceries")
        writes: list[tuple[str, str, str]] = []  # (writer_id, action, entity_id)

        for token, owner in ((alice, alice_id), (bob, bob_id)):
            expense = _create(client, token, _valid_body(groceries, amount="10.00"))
            writes.append((owner, "CREATE", expense["id"]))
            assert (
                client.put(
                    f"/api/v1/expenses/{expense['id']}",
                    json={"amount": "11.00"},
                    headers=_auth(token),
                ).status_code
                == 200
            )
            writes.append((owner, "UPDATE", expense["id"]))
            assert (
                client.delete(f"/api/v1/expenses/{expense['id']}", headers=_auth(token)).status_code
                == 204
            )
            writes.append((owner, "DELETE", expense["id"]))
            month = "2026-06" if owner == alice_id else "2026-07"
            assert _put_budget(client, token, month, "500.00").status_code == 200
            budget_entity = _budget_id(override, owner, month)
            writes.append((owner, "CREATE", budget_entity))
            assert (
                client.delete(f"/api/v1/budgets/{month}", headers=_auth(token)).status_code == 204
            )
            writes.append((owner, "DELETE", budget_entity))
            # Category writes happen too and must produce NO audit row.
            category_id = _create_category(client, token, f"Cat{owner[:6]}")
            assert (
                client.delete(
                    f"/api/v1/categories/{category_id}", headers=_auth(token)
                ).status_code
                == 204
            )

        # Read the audit trail through a FRESH session, not app internals.
        with next(override()) as session:
            rows = session.scalars(select(AuditLog)).all()
        assert len(rows) == len(writes)
        assert {row.entity_type for row in rows} == {"expense", "budget"}
        observed: list[tuple[str, str, str]] = []
        for row in rows:
            assert row.action in {"CREATE", "UPDATE", "DELETE"}
            observed.append((str(row.user_id), row.action, str(row.entity_id)))
        # Every successful write has EXACTLY ONE row for its writer/entity.
        for write in writes:
            assert observed.count(write) == 1, (write, observed)
        # No row is ever attributed to the other user's writes.
        assert sorted(observed) == sorted(writes)
        assert {o[0] for o in observed} == {alice_id, bob_id}
        # Categories write NO audit row (ck_audit_entity_type).
        with next(override()) as session:
            category_rows = session.scalars(
                select(AuditLog).where(AuditLog.entity_type == "category")
            ).all()
        assert category_rows == []
