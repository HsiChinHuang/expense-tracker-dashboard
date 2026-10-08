# mypy: disable-error-code="import-untyped"
"""Integration tests for /api/v1/categories (t11, REQ-API-030/031/032).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

The harness is a COPY of the merged t8 pattern from
tests/integration/test_auth_api.py (that module is not a shared fixture
library and there is no tests/conftest.py). Isolation follows the groom
pin: one private SQLite file PER TEST under ``tmp_path``, schema via
``Base.metadata.create_all`` (NOT alembic), app isolation through
``dependency_overrides[get_db]``, and the ten system rows provisioned by
calling ``seed_system_categories`` directly with an explicit commit
(mirroring tests/unit/test_category_seed.py). Reading
``os.environ["DATABASE_URL"]`` is forbidden: ac2 runs four nodes and ac3
six in one pytest process.
"""

import uuid
from collections.abc import Callable, Generator, Iterator
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
from app.models.category import Category
from app.scripts.seed import SYSTEM_CATEGORIES, seed_system_categories

CATEGORY_FIELDS = {"id", "name", "color", "icon", "is_system", "created_at"}
ERROR_FIELDS = {"detail", "code", "field"}
TEST_SECRET = "categories-integration-secret-not-a-real-key"

SYSTEM_NAMES_ORDERED = sorted(entry["name"] for entry in SYSTEM_CATEGORIES)
"""The ten seeded names in the order ac1's listing must show them."""


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
        override generator function itself (tests mutate rows with
        ``with next(override()) as session:``).
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / 't11_test.db').as_posix()}")
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


def _system_ids(override: Callable[[], Generator[Session, None, None]]) -> dict[str, str]:
    """Return {name: id-string} for every seeded system category.

    Args:
        override: The ``get_db`` override generator function.

    Returns:
        dict[str, str]: Mapping from system name to canonical id string.
    """
    with next(override()) as session:
        rows = session.execute(
            select(Category.name, Category.id).where(Category.is_system.is_(True))
        ).all()
    return {str(name): str(value) for name, value in rows}


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
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200
    return cast("str", cast("dict[str, Any]", response.json())["access_token"])


def _auth(token: str) -> dict[str, str]:
    """Return the bearer Authorization header for ``token``.

    Args:
        token: JWT access token.

    Returns:
        dict[str, str]: Headers for the TestClient call.
    """
    return {"Authorization": f"Bearer {token}"}


def _create(client: TestClient, token: str, payload: dict[str, Any]) -> Any:
    """POST /api/v1/categories and return the raw response.

    Args:
        client: Isolated test client.
        token: Caller's access token.
        payload: Create body.

    Returns:
        Any: The httpx Response object.
    """
    return client.post("/api/v1/categories", json=payload, headers=_auth(token))


def _count_rows(
    override: Callable[[], Generator[Session, None, None]],
    *,
    name: str,
    user_id: str | None = None,
) -> int:
    """Count category rows by case-folded name and optional owner.

    Args:
        override: The ``get_db`` override generator function.
        name: Name to match case-insensitively.
        user_id: Owner id string, or ``None`` to match any owner.

    Returns:
        int: Number of matching rows.
    """
    statement = select(func.count()).select_from(Category).where(
        func.lower(Category.name) == name.lower()
    )
    with next(override()) as session:
        if user_id is not None:
            statement = statement.where(Category.user_id == uuid.UUID(user_id))
        return int(session.scalar(statement) or 0)


class TestCategoriesApi:
    """Contract coverage for GET/POST/DELETE /api/v1/categories."""

    def test_list_returns_system_plus_own_custom_only_with_exact_fields_and_order(
        self, tmp_path: Path
    ) -> None:
        """GET returns the wrapper, system+own only, six fields, pinned order."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")

        assert _create(client, alice, {"name": "Zebra", "color": "#112233"}).status_code == 201
        assert _create(client, alice, {"name": "apple", "color": "#445566"}).status_code == 201
        assert _create(client, bob, {"name": "BobSecret", "color": "#778899"}).status_code == 201

        response = client.get("/api/v1/categories", headers=_auth(alice))

        assert response.status_code == 200
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == {"categories"}
        items = body["categories"]
        assert len(items) == 12
        for item in items:
            assert set(item.keys()) == CATEGORY_FIELDS
            assert "user_id" not in item
        names = [str(item["name"]) for item in items]
        assert names[:10] == SYSTEM_NAMES_ORDERED
        assert names[10:] == ["apple", "Zebra"]
        assert all(item["is_system"] is True for item in items[:10])
        assert all(item["is_system"] is False for item in items[10:])
        assert "BobSecret" not in names

    def test_list_without_token_returns_401_unauthorized_contract_shape(
        self, tmp_path: Path
    ) -> None:
        """No Authorization header maps to 401 UNAUTHORIZED (merged 401)."""
        client, override = _make_client(tmp_path)
        _seed(override)

        response = client.get("/api/v1/categories")

        assert response.status_code == 401
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "UNAUTHORIZED"

    def test_create_valid_returns_201_with_exact_shape_and_owner_id(
        self, tmp_path: Path
    ) -> None:
        """201 echoes the six fields, icon (null when omitted), row owned."""
        client, override = _make_client(tmp_path)
        _seed(override)
        registered = _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        with_icon = _create(client, token, {"name": "Pets", "color": "#00ff00", "icon": "dog"})
        without_icon = _create(client, token, {"name": "Crypto", "color": "#ABCDEF"})

        assert with_icon.status_code == 201
        created = cast("dict[str, Any]", with_icon.json())
        assert set(created.keys()) == CATEGORY_FIELDS
        assert created["name"] == "Pets"
        assert created["color"] == "#00ff00"
        assert created["icon"] == "dog"
        assert created["is_system"] is False
        assert isinstance(created["created_at"], str)

        assert without_icon.status_code == 201
        assert cast("dict[str, Any]", without_icon.json())["icon"] is None

        with next(override()) as session:
            row = session.scalars(
                select(Category).where(Category.name == "Pets")
            ).one()
            assert str(row.user_id) == registered["id"]
            assert row.is_system is False
            assert row.icon == "dog"

    def test_create_duplicate_own_name_case_insensitive_returns_409_duplicate_category_field_name(
        self, tmp_path: Path
    ) -> None:
        """A case-variant of the caller's own name 409s and stores nothing."""
        client, override = _make_client(tmp_path)
        _seed(override)
        registered = _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        assert _create(client, token, {"name": "Gym Gear", "color": "#111111"}).status_code == 201

        response = _create(client, token, {"name": "gym gear", "color": "#222222"})

        assert response.status_code == 409
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "DUPLICATE_CATEGORY"
        assert body["field"] == "name"
        assert _count_rows(override, name="gym gear", user_id=registered["id"]) == 1

    def test_create_duplicate_system_name_returns_409_and_a_different_user_may_reuse_a_custom_name(
        self, tmp_path: Path
    ) -> None:
        """System names are reserved; another user's custom name is not."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")

        assert _create(client, alice, {"name": "Sailing", "color": "#123456"}).status_code == 201

        system_variant = _create(client, alice, {"name": "GROCERIES", "color": "#123456"})
        assert system_variant.status_code == 409
        system_body = cast("dict[str, Any]", system_variant.json())
        assert set(system_body.keys()) == ERROR_FIELDS
        assert system_body["code"] == "DUPLICATE_CATEGORY"
        assert system_body["field"] == "name"
        assert _count_rows(override, name="groceries") == 1

        reuse = _create(client, bob, {"name": "sailing", "color": "#654321"})
        assert reuse.status_code == 201
        assert cast("dict[str, Any]", reuse.json())["is_system"] is False

    @pytest.mark.parametrize(
        ("payload", "expected_field"),
        [
            ({"name": "Bad", "color": "red"}, "color"),
            ({"name": "Bad", "color": "#GGGGGG"}, "color"),
            ({"name": "Bad", "color": "#12345"}, "color"),
            ({"name": "x" * 101, "color": "#123456"}, "name"),
            ({"name": "", "color": "#123456"}, "name"),
            ({"color": "#123456"}, "name"),
            ({"name": "NoColor"}, "color"),
        ],
    )
    def test_create_invalid_bodies_return_422_validation_error_with_field(
        self, tmp_path: Path, payload: dict[str, Any], expected_field: str
    ) -> None:
        """Each malformed member yields 422 VALIDATION_ERROR with field."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")

        response = _create(client, token, payload)

        assert response.status_code == 422, payload
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_FIELDS, payload
        assert body["code"] == "VALIDATION_ERROR", payload
        assert body["field"] == expected_field, payload
        assert _count_rows(override, name=str(payload.get("name", "no-such-name"))) == 0

    def test_delete_own_unused_returns_204_and_row_is_gone(self, tmp_path: Path) -> None:
        """204 with an empty body removes the caller's custom row."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        temp = _create(client, token, {"name": "Temp", "color": "#123abc"})
        created = cast("dict[str, Any]", temp.json())

        response = client.delete(f"/api/v1/categories/{created['id']}", headers=_auth(token))

        assert response.status_code == 204
        assert response.content == b""
        assert _count_rows(override, name="temp") == 0

    def test_delete_unknown_and_cross_user_return_404_not_found_contract_shape(
        self, tmp_path: Path
    ) -> None:
        """Unknown and other-user ids are 404 NOT_FOUND, never 403."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        _register(client, "bob@example.com", "bob")
        alice = _login(client, "alice@example.com")
        bob = _login(client, "bob@example.com")
        private = _create(client, bob, {"name": "Private", "color": "#abcdef"})
        bob_row = cast("dict[str, Any]", private.json())

        unknown = client.delete(f"/api/v1/categories/{uuid.uuid4()}", headers=_auth(alice))
        cross_user = client.delete(f"/api/v1/categories/{bob_row['id']}", headers=_auth(alice))

        for response in (unknown, cross_user):
            assert response.status_code == 404
            body = cast("dict[str, Any]", response.json())
            assert set(body.keys()) == ERROR_FIELDS
            assert body["code"] == "NOT_FOUND"
        assert _count_rows(override, name="private") == 1

    def test_delete_system_category_returns_404_and_row_survives(self, tmp_path: Path) -> None:
        """System categories are not deletable: 404 and the row survives."""
        client, override = _make_client(tmp_path)
        _seed(override)
        _register(client, "alice@example.com", "alice")
        token = _login(client, "alice@example.com")
        system_id = _system_ids(override)["Groceries"]

        response = client.delete(f"/api/v1/categories/{system_id}", headers=_auth(token))

        assert response.status_code == 404
        assert response.status_code != 409
        body = cast("dict[str, Any]", response.json())
        assert set(body.keys()) == ERROR_FIELDS
        assert body["code"] == "CATEGORY_NOT_FOUND"
        assert body["field"] == "category_id"
        assert _count_rows(override, name="groceries") == 1

    def test_openapi_has_no_update_route_for_categories(self, tmp_path: Path) -> None:
        """No PATCH/PUT anywhere, no POST on the item path (immutability)."""
        client, override = _make_client(tmp_path)
        _seed(override)

        schema = cast("dict[str, Any]", client.get("/openapi.json").json())
        paths = cast("dict[str, Any]", schema["paths"])
        category_paths = {
            key: value for key, value in paths.items() if key.startswith("/api/v1/categories")
        }

        assert set(category_paths) == {"/api/v1/categories", "/api/v1/categories/{category_id}"}
        for operations in category_paths.values():
            for forbidden in ("patch", "put"):
                assert forbidden not in operations
        assert "post" not in category_paths["/api/v1/categories/{category_id}"]
        # sanity (non-vacuous): the create operation itself is present.
        assert "post" in category_paths["/api/v1/categories"]

    def test_openapi_lists_three_category_operations_after_auth_paths(
        self, tmp_path: Path
    ) -> None:
        """OpenAPI lists get/post/delete and categories follow the auth paths."""
        client, override = _make_client(tmp_path)
        _seed(override)

        schema = cast("dict[str, Any]", client.get("/openapi.json").json())
        paths = cast("dict[str, Any]", schema["paths"])
        keys = list(paths.keys())

        assert set(p for p in keys if p.startswith("/api/v1/categories")) == {
            "/api/v1/categories",
            "/api/v1/categories/{category_id}",
        }
        assert set(paths["/api/v1/categories"].keys()) == {"get", "post"}
        assert set(paths["/api/v1/categories/{category_id}"].keys()) == {"delete"}
        for auth_path in ("/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/auth/me"):
            assert auth_path in paths
            assert keys.index(auth_path) < keys.index("/api/v1/categories")
