# mypy: disable-error-code="import-untyped"
"""Unit tests for app.services.category_service (t11, REQ-BE-062/063).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation follows the groom pin: one private SQLite file PER TEST under
``tmp_path`` (named after the test), ``Base.metadata.create_all`` (NOT
alembic), and no read of ``os.environ["DATABASE_URL"]``. The service is
called directly — the HTTP layer lives in the integration module.

The in-use 409 is the review_plan W3 seam: ``count_expenses_for_category``
is monkeypatched on the service module (its real body imports
``app.models.expense``, which only t13 lands), so the pinned nodes prove
both branches — count 1 raises 409 CATEGORY_IN_USE and count 0 deletes —
and the pair cannot pass vacuously on a broken delete.
"""

import uuid
from pathlib import Path

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import CATEGORY_IN_USE, CATEGORY_NOT_FOUND, AppError
from app.database import create_db_engine, create_session_factory
from app.models import Base
from app.models.category import Category
from app.models.user import User
from app.services import category_service
from app.services.category_service import validate_category_access


def _session(tmp_path: Path, name: str) -> Session:
    """Return a Session over this test's own SQLite file and schema.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Session: A fresh session with users + categories created.
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = create_session_factory(engine)
    return factory()


def _add_user(session: Session, email: str) -> User:
    """Persist a user row and return it.

    Args:
        session: Active session.
        email: Unique email for the account.

    Returns:
        User: The persisted row.
    """
    user = User(email=email, username=email.split("@")[0], hashed_password="x")
    session.add(user)
    session.commit()
    return user


def _add_category(
    session: Session,
    name: str,
    *,
    user_id: uuid.UUID | None,
    is_system: bool = False,
) -> Category:
    """Persist a category row and return it.

    Args:
        session: Active session.
        name: Category name.
        user_id: Owner id, or ``None`` for system rows.
        is_system: System flag (must pair with ``user_id is None``).

    Returns:
        Category: The persisted row.
    """
    category = Category(name=name, color="#112233", icon=None, is_system=is_system, user_id=user_id)
    session.add(category)
    session.commit()
    return category


def _row_count(session: Session, category_id: uuid.UUID) -> int:
    """Count surviving category rows with the given id.

    Args:
        session: Active session.
        category_id: Category primary key to look up.

    Returns:
        int: 1 when the row still exists, else 0.
    """
    return int(
        session.scalar(select(func.count()).select_from(Category).where(Category.id == category_id))
        or 0
    )


class TestValidateCategoryAccess:
    """Contract coverage for validate_category_access (t11 ac4)."""

    def test_system_category_is_returned_for_any_user(self, tmp_path: Path) -> None:
        """A system row is usable by a caller who does not own it."""
        session = _session(tmp_path, "test_system_category_is_returned_for_any_user")
        with session:
            alice = _add_user(session, "alice@example.com")
            system = _add_category(session, "Groceries", user_id=None, is_system=True)

            result = validate_category_access(session, alice, system.id)

            assert result.id == system.id
            assert result.is_system is True

    def test_own_custom_category_is_returned(self, tmp_path: Path) -> None:
        """The caller's own custom row is returned unchanged."""
        session = _session(tmp_path, "test_own_custom_category_is_returned")
        with session:
            alice = _add_user(session, "alice@example.com")
            own = _add_category(session, "Pets", user_id=alice.id)

            result = validate_category_access(session, alice, own.id)

            assert result.id == own.id
            assert result.user_id == alice.id

    def test_other_users_custom_category_raises_404_category_not_found(
        self, tmp_path: Path
    ) -> None:
        """Another user's row is 404 CATEGORY_NOT_FOUND, never 403."""
        session = _session(
            tmp_path, "test_other_users_custom_category_raises_404_category_not_found"
        )
        with session:
            alice = _add_user(session, "alice@example.com")
            bob = _add_user(session, "bob@example.com")
            bobs = _add_category(session, "Private", user_id=bob.id)

            with pytest.raises(AppError) as excinfo:
                validate_category_access(session, alice, bobs.id)

            error = excinfo.value
            assert error.status_code == 404
            assert error.status_code != 403
            assert error.code == CATEGORY_NOT_FOUND
            assert error.field == "category_id"

    def test_unknown_id_raises_404_category_not_found(self, tmp_path: Path) -> None:
        """A random uuid raises the same 404 as a cross-user id."""
        session = _session(tmp_path, "test_unknown_id_raises_404_category_not_found")
        with session:
            alice = _add_user(session, "alice@example.com")

            with pytest.raises(AppError) as excinfo:
                validate_category_access(session, alice, uuid.uuid4())

            error = excinfo.value
            assert error.status_code == 404
            assert error.code == CATEGORY_NOT_FOUND
            assert error.field == "category_id"


class TestDeleteCategoryInUse:
    """W3 seam coverage for delete_category's expense-count 409 (t11 ac3)."""

    def test_expense_count_one_raises_409_category_in_use(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Monkeypatched count 1 -> 409 CATEGORY_IN_USE, row survives."""
        session = _session(tmp_path, "test_expense_count_one_raises_409_category_in_use")
        with session:
            alice = _add_user(session, "alice@example.com")
            pet = _add_category(session, "Pets", user_id=alice.id)

            def fake_count(_session: Session, category_id: uuid.UUID) -> int:
                """Return a fixed in-use count for the W3 seam.

                Args:
                    _session: Ignored session.
                    category_id: Ignored category id.

                Returns:
                    int: Always 1.
                """
                return 1

            monkeypatch.setattr(category_service, "count_expenses_for_category", fake_count)

            with pytest.raises(AppError) as excinfo:
                category_service.delete_category(session, alice, pet.id)

            error = excinfo.value
            assert error.status_code == 409
            assert error.code == CATEGORY_IN_USE
            assert error.field == "category_id"
            assert _row_count(session, pet.id) == 1

    def test_expense_count_zero_deletes_and_never_blocks(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Monkeypatched count 0 -> the row is deleted (non-vacuous pair)."""
        session = _session(tmp_path, "test_expense_count_zero_deletes_and_never_blocks")
        with session:
            alice = _add_user(session, "alice@example.com")
            pet = _add_category(session, "Pets", user_id=alice.id)

            def fake_count(_session: Session, category_id: uuid.UUID) -> int:
                """Return a fixed unused count for the W3 seam.

                Args:
                    _session: Ignored session.
                    category_id: Ignored category id.

                Returns:
                    int: Always 0.
                """
                return 0

            monkeypatch.setattr(category_service, "count_expenses_for_category", fake_count)

            category_service.delete_category(session, alice, pet.id)

            assert _row_count(session, pet.id) == 0
