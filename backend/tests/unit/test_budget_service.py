"""Unit tests for app.services.budget_service (t14 ac5, REQ-ARCH-078/083).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation follows the merged t13 unit pattern (no conftest.py): one
private SQLite file PER TEST under ``tmp_path``, schema via
``Base.metadata.create_all``. Assertions run against PERSISTED content
read back through a FRESH session (never in-session identity), because
the contract under test is what one commit lands.

The rollback node is the review_plan W7 PINNED mechanism: the service
imports ``write_audit_log`` unqualified (Chapter 6 6.9.1's call shape),
so monkeypatching ``app.services.budget_service.write_audit_log`` with a
stub staging an AuditLog whose ``action="PATCH"`` violates
ck_audit_action at the service's single commit. ``entity_type`` stays
the valid 'budget' (no out-of-CHECK value is invented, no monkeypatched
``raise`` variant). t12 ac3 remains the MACHINERY proof; this module
proves the budget-write INTEGRATION only.

The audit payload is the byte-pinned budget shape (review_plan W5,
Chapter 6 6.9.4): EXACTLY ``{amount, year_month}``, both strings.
"""

import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
from sqlalchemy import Engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import AppError
from app.database import create_db_engine
from app.models import Base
from app.models.audit_log import AuditLog
from app.models.budget import Budget
from app.models.user import User
from app.services import budget_service

PAYLOAD_KEYS = {"amount", "year_month"}


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


def _seed(tmp_path: Path, name: str) -> tuple[sessionmaker[Session], User]:
    """Persist one user, return the factory and the user handle.

    Args:
        tmp_path: pytest-provided directory.
        name: Database file name for this test.

    Returns:
        tuple: The session factory and the persisted user.
    """
    _, factory = _session(tmp_path, name)
    with factory() as session:
        user = User(email="alice@example.com", username="alice", hashed_password="x")
        session.add(user)
        session.commit()
    return factory, user


def _audit_rows(factory: sessionmaker[Session]) -> list[AuditLog]:
    """Read every persisted audit row through a FRESH session.

    Args:
        factory: This test's session factory.

    Returns:
        list[AuditLog]: All audit rows in the database.
    """
    with factory() as session:
        return list(session.scalars(select(AuditLog)).all())


def _cast_dict(value: object) -> dict[str, Any]:
    """Narrow a persisted JSON column to a dict for assertions.

    Args:
        value: The persisted ``old_value``/``new_value`` column.

    Returns:
        dict[str, Any]: The mapped payload.
    """
    return cast("dict[str, Any]", value)


class TestBudgetAuditIntegration:
    """Same-transaction audit integration through the real service."""

    def test_create_persists_audit_row_with_create_action_null_old_value_and_exact_budget_payload(
        self, tmp_path: Path
    ) -> None:
        """set_budget (first write) lands budget + CREATE audit row at once."""
        factory, user = _seed(tmp_path, "audit_create")
        with factory() as session:
            budget = budget_service.set_budget(
                session,
                user,
                year_month="2026-10",
                amount="2000.00",
                ip_address="203.0.113.7",
            )
            budget_id = budget.id

        rows = _audit_rows(factory)
        assert len(rows) == 1
        row = rows[0]
        assert row.action == "CREATE"
        assert row.entity_type == "budget"  # IN-CHECK (ck_audit_entity_type)
        assert row.entity_id == budget_id
        assert row.user_id == user.id
        assert row.old_value is None
        new_value = _cast_dict(row.new_value)
        assert set(new_value.keys()) == PAYLOAD_KEYS  # byte-pinned W5
        assert new_value == {"amount": "2000.00", "year_month": "2026-10"}
        assert isinstance(new_value["amount"], str)
        assert isinstance(new_value["year_month"], str)
        assert row.ip_address == "203.0.113.7"
        with factory() as session:
            stored = session.scalars(select(Budget)).one()
            assert stored.id == budget_id
            assert stored.amount.quantize(Decimal("0.01")) == Decimal("2000.00")

    def test_update_persists_audit_row_with_both_values_and_exact_budget_payload_keys(
        self, tmp_path: Path
    ) -> None:
        """The second PUT writes an UPDATE row; BOTH audits share one budget."""
        factory, user = _seed(tmp_path, "audit_update")
        with factory() as session:
            budget = budget_service.set_budget(
                session, user, year_month="2026-10", amount="2000.00"
            )
            budget_id = budget.id
        with factory() as session:
            budget_service.set_budget(
                session, user, year_month="2026-10", amount="2500.50"
            )

        rows = _audit_rows(factory)
        assert len(rows) == 2  # create AND update rows both persist
        actions = {row.action for row in rows}
        assert actions == {"CREATE", "UPDATE"}
        update = next(row for row in rows if row.action == "UPDATE")
        assert update.entity_type == "budget"
        assert update.entity_id == budget_id
        old_value = _cast_dict(update.old_value)
        new_value = _cast_dict(update.new_value)
        assert set(old_value.keys()) == PAYLOAD_KEYS
        assert set(new_value.keys()) == PAYLOAD_KEYS
        assert old_value == {"amount": "2000.00", "year_month": "2026-10"}
        assert new_value == {"amount": "2500.50", "year_month": "2026-10"}
        assert old_value["amount"] != new_value["amount"]
        # upsert: ONE budget row carries both audit rows
        with factory() as session:
            budgets = session.scalars(select(Budget)).all()
            assert len(budgets) == 1
            assert budgets[0].amount.quantize(Decimal("0.01")) == Decimal("2500.50")

    def test_delete_persists_audit_row_with_old_value_and_null_new_value(
        self, tmp_path: Path
    ) -> None:
        """delete_budget lands the DELETE audit row in the same commit."""
        factory, user = _seed(tmp_path, "audit_delete")
        with factory() as session:
            budget = budget_service.set_budget(
                session, user, year_month="2026-10", amount="7.00"
            )
            budget_id = budget.id
        with factory() as session:
            budget_service.delete_budget(session, user, year_month="2026-10")

        rows = _audit_rows(factory)
        assert len(rows) == 2
        delete = next(row for row in rows if row.action == "DELETE")
        assert delete.entity_type == "budget"
        assert delete.entity_id == budget_id
        assert delete.new_value is None
        old_value = _cast_dict(delete.old_value)
        assert set(old_value.keys()) == PAYLOAD_KEYS
        assert old_value == {"amount": "7.00", "year_month": "2026-10"}
        with factory() as session:
            assert session.scalars(select(Budget)).first() is None

        # deleting an absent month afterwards is the frozen 404, no new row
        with factory() as session:
            with pytest.raises(AppError) as excinfo:
                budget_service.delete_budget(session, user, year_month="2026-10")
            assert excinfo.value.status_code == 404
            assert excinfo.value.code == "NOT_FOUND"
        assert len(_audit_rows(factory)) == 2

    def test_action_check_violation_in_the_service_transaction_rolls_back_the_budget_write(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """W7 pinned: a bad audit action rolls the budget write back too.

        The stub stages a REAL AuditLog with action="PATCH" (violates
        ck_audit_action; entity_type stays the valid 'budget'). The
        service's single commit raises IntegrityError and a fresh
        session shows NEITHER the budget NOR any audit row. t12 ac3 is
        the machinery proof; this node proves integration.
        """
        factory, user = _seed(tmp_path, "audit_rollback")

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
                entity_type: Kept valid ('budget') per the pinned W7.
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

        monkeypatch.setattr(budget_service, "write_audit_log", poisoned_writer)

        with factory() as session:
            with pytest.raises(IntegrityError):
                budget_service.set_budget(
                    session, user, year_month="2026-10", amount="10.00"
                )

        with factory() as session:
            assert session.scalars(select(Budget)).first() is None
            assert session.scalars(select(AuditLog)).first() is None
