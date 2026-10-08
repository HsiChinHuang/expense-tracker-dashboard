"""Unit tests for app.services.expense_service (t13 ac5).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation follows the merged t11 unit pattern (no conftest.py): one
private SQLite file PER TEST under ``tmp_path``, schema via
``Base.metadata.create_all``. Assertions run against PERSISTED content
read back through a FRESH session (never in-session identity), because
the contract under test is what one commit lands.

The rollback node is the review_plan W7 PINNED mechanism: the service
imports ``write_audit_log`` unqualified, so monkeypatching
``app.services.expense_service.write_audit_log`` with a stub staging an
AuditLog whose ``action="PATCH"`` violates ck_audit_action at the
service's single commit. ``entity_type`` stays the valid 'expense' (no
out-of-CHECK value is invented). t12 ac3 remains the MACHINERY proof;
this module proves the expense-write INTEGRATION only.

TestCategoryInUseWithRealExpenses proves the retired W3 seam: the
delete-in-use 409 now runs the REAL count query (no monkeypatching of
count_expenses_for_category anywhere in this module).
"""

import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import CATEGORY_IN_USE, AppError
from app.database import create_db_engine
from app.models import Base
from app.models.audit_log import AuditLog
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User
from app.services import category_service, expense_service

PAYLOAD_KEYS = {"amount", "date", "category_id", "note"}


def _session(tmp_path: Path, name: str) -> tuple[Engine, sessionmaker[Session]]:
    """Create this test's SQLite file/schema and its session factory.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        tuple[Engine, sessionmaker[Session]]: Engine plus factory; fresh
        sessions come from the factory, never the writer's session.
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


def _seed(tmp_path: Path, name: str) -> tuple[sessionmaker[Session], User, Category]:
    """Persist one user and one custom category, return fresh handles.

    Args:
        tmp_path: pytest-provided directory.
        name: Database file name for this test.

    Returns:
        tuple: The factory, the user, and the caller's category.
    """
    _, factory = _session(tmp_path, name)
    with factory() as session:
        user = User(email="alice@example.com", username="alice", hashed_password="x")
        session.add(user)
        session.commit()
        category = Category(name="Pets", color="#112233", user_id=user.id)
        session.add(category)
        session.commit()
    return factory, user, category


def _audit_rows(factory: sessionmaker[Session]) -> list[AuditLog]:
    """Read every persisted audit row through a FRESH session.

    Args:
        factory: This test's session factory.

    Returns:
        list[AuditLog]: All audit rows in the database.
    """
    with factory() as session:
        return list(session.scalars(select(AuditLog)).all())


class TestExpenseAuditIntegration:
    """Same-transaction audit integration through the real service."""

    def test_create_persists_audit_row_with_create_action_null_old_value_and_exact_expense_payload(
        self, tmp_path: Path
    ) -> None:
        """create_expense lands expense + CREATE audit row in ONE commit."""
        factory, user, category = _seed(tmp_path, "audit_create")
        with factory() as session:
            expense = expense_service.create_expense(
                session,
                user,
                amount="125.5",
                category_id=category.id,
                date=date(2026, 1, 15),
                note="shop",
                ip_address="203.0.113.7",
            )
            expense_id = expense.id

        rows = _audit_rows(factory)
        assert len(rows) == 1
        row = rows[0]
        assert row.action == "CREATE"
        assert row.entity_type == "expense"
        assert row.entity_id == expense_id
        assert row.user_id == user.id
        assert row.old_value is None
        assert isinstance(row.new_value, dict)
        assert set(row.new_value.keys()) == PAYLOAD_KEYS
        assert row.new_value == {
            "amount": "125.50",
            "date": "2026-01-15",
            "category_id": str(category.id),
            "note": "shop",
        }
        assert row.ip_address == "203.0.113.7"
        with factory() as session:
            stored = session.scalars(select(Expense)).one()
            assert stored.id == expense_id
            assert stored.amount.quantize(Decimal("0.01")) == Decimal("125.50")

    def test_update_persists_audit_row_with_both_values_and_exact_payload_keys(
        self, tmp_path: Path
    ) -> None:
        """update_expense audits old AND new payloads with differing amounts."""
        factory, user, category = _seed(tmp_path, "audit_update")
        with factory() as session:
            expense = expense_service.create_expense(
                session,
                user,
                amount="10.00",
                category_id=category.id,
                date=date(2026, 1, 1),
                note=None,
            )
            expense_id = expense.id
        with factory() as session:
            expense_service.update_expense(
                session,
                user,
                expense_id,
                amount="22.45",
                note_sent=False,
            )

        rows = _audit_rows(factory)
        assert len(rows) == 2
        update = rows[1]
        assert update.action == "UPDATE"
        assert update.entity_type == "expense"
        assert update.entity_id == expense_id
        old = cast_dict(update.old_value)
        new = cast_dict(update.new_value)
        assert set(old.keys()) == PAYLOAD_KEYS
        assert set(new.keys()) == PAYLOAD_KEYS
        assert old["amount"] == "10.00"
        assert new["amount"] == "22.45"
        assert old["amount"] != new["amount"]
        assert old["note"] is None and new["note"] is None
        assert old["date"] == "2026-01-01" == new["date"]

    def test_delete_persists_audit_row_with_old_value_and_null_new_value(
        self, tmp_path: Path
    ) -> None:
        """delete_expense audits old_value only; the expense row is gone."""
        factory, user, category = _seed(tmp_path, "audit_delete")
        with factory() as session:
            expense = expense_service.create_expense(
                session,
                user,
                amount="7.00",
                category_id=category.id,
                date=date(2026, 3, 4),
                note="bye",
            )
            expense_id = expense.id
        with factory() as session:
            expense_service.delete_expense(session, user, expense_id)

        rows = _audit_rows(factory)
        assert len(rows) == 2
        delete = rows[1]
        assert delete.action == "DELETE"
        assert delete.entity_type == "expense"
        assert delete.entity_id == expense_id
        assert delete.new_value is None
        old = cast_dict(delete.old_value)
        assert set(old.keys()) == PAYLOAD_KEYS
        assert old == {
            "amount": "7.00",
            "date": "2026-03-04",
            "category_id": str(category.id),
            "note": "bye",
        }
        with factory() as session:
            assert session.scalars(select(Expense)).first() is None

    def test_action_check_violation_in_the_service_transaction_rolls_back_the_expense_write(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """W7 pinned: a bad audit action rolls the expense write back too.

        The stub stages a REAL AuditLog with action="PATCH" (violates
        ck_audit_action; entity_type stays the valid 'expense'). The
        service's single commit raises IntegrityError and a fresh
        session shows NEITHER the expense NOR any audit row. t12 ac3 is
        the machinery proof; this node proves integration.
        """
        factory, user, category = _seed(tmp_path, "audit_rollback")

        def poisoned_writer(
            db: Session,
            user_id: uuid.UUID,
            action: str,
            entity_type: str,
            entity_id: uuid.UUID,
            old_value: dict[str, Any] | None,
            new_value: dict[str, Any] | None,
            ip_address: str | None,
        ) -> None:
            """Stage an AuditLog whose action violates ck_audit_action.

            Args:
                db: The caller's session (the one that will commit).
                user_id: Acting user id.
                action: Ignored; replaced with the invalid 'PATCH'.
                entity_type: Kept valid ('expense') per the pinned W7.
                entity_id: Entity id.
                old_value: Pre-change payload.
                new_value: Post-change payload.
                ip_address: Client IP.

            Returns:
                None
            """
            db.add(
                AuditLog(
                    user_id=user_id,
                    action="PATCH",
                    entity_type=entity_type,
                    entity_id=entity_id,
                    old_value=old_value,
                    new_value=new_value,
                    ip_address=ip_address,
                )
            )

        monkeypatch.setattr(expense_service, "write_audit_log", poisoned_writer)

        with factory() as session:
            with pytest.raises(IntegrityError):
                expense_service.create_expense(
                    session,
                    user,
                    amount="10.00",
                    category_id=category.id,
                    date=date(2026, 1, 1),
                    note=None,
                )

        with factory() as session:
            assert session.scalars(select(Expense)).first() is None
            assert session.scalars(select(AuditLog)).first() is None


class TestCategoryInUseWithRealExpenses:
    """W3 seam retired: the REAL expense count drives the 409."""

    def test_deleting_a_category_with_a_real_expense_raises_409_category_in_use(
        self, tmp_path: Path
    ) -> None:
        """A real expense row makes the service 409 CATEGORY_IN_USE."""
        factory, user, category = _seed(tmp_path, "in_use_409")
        with factory() as session:
            expense_service.create_expense(
                session,
                user,
                amount="3.00",
                category_id=category.id,
                date=date(2026, 1, 2),
                note=None,
            )

        with factory() as session:
            with pytest.raises(AppError) as excinfo:
                category_service.delete_category(session, user, category.id)

        error = excinfo.value
        assert error.status_code == 409
        assert error.code == CATEGORY_IN_USE
        assert error.field == "category_id"
        with factory() as session:
            assert session.scalars(
                select(Category).where(Category.id == category.id)
            ).first() is not None

    def test_deleting_an_unused_category_still_succeeds_after_the_real_count_lands(
        self, tmp_path: Path
    ) -> None:
        """Non-vacuous pair: zero real expenses -> delete succeeds."""
        factory, user, category = _seed(tmp_path, "unused_delete")
        with factory() as session:
            other = Category(name="Empty", color="#223344", user_id=user.id)
            session.add(other)
            session.commit()
            other_id = other.id

        with factory() as session:
            category_service.delete_category(session, user, other_id)

        with factory() as session:
            assert session.scalars(select(Category).where(Category.id == other_id)).first() is None
            # the used category from the pair above is untouched semantics:
            # this test's own category still exists (no cascade surprises)
            assert session.scalars(
                select(Category).where(Category.id == category.id)
            ).first() is not None


def cast_dict(value: object) -> dict[str, Any]:
    """Narrow a persisted JSON column to a dict for assertions.

    Args:
        value: The persisted value (must be a dict).

    Returns:
        dict[str, Any]: The same value, typed.

    Raises:
        AssertionError: When the value is not a dict.
    """
    assert isinstance(value, dict)
    return value


__all__ = ["TestCategoryInUseWithRealExpenses", "TestExpenseAuditIntegration"]
