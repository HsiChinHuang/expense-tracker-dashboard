"""Unit tests for the same-transaction audit writer (t12 ac2/ac3/ac4).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation contract (docs/issues/t12.md): one SQLite file PER TEST under
``tmp_path``, named after the test (COPY of the
tests/unit/test_category_model.py harness; no conftest.py exists).
Payload key sets are the review_plan W5 pins — expense EXACTLY
{amount, date, category_id, note}, budget EXACTLY {amount, year_month} —
and every assertion checks persisted CONTENT through a fresh session,
never a row count (vacuous-trap guard).
"""

import uuid
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit.logger import get_audit_logger, write_audit_log
from app.database import create_db_engine, create_session_factory
from app.main import app
from app.models import AuditLog, Base, Category, User

EXPENSE_PAYLOAD: dict[str, Any] = {
    "amount": "125.50",
    "date": "2026-01-15",
    "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "note": "Team lunch",
}
BUDGET_PAYLOAD: dict[str, Any] = {"amount": "800.00", "year_month": "2026-01"}
BUDGET_PAYLOAD_OLD: dict[str, Any] = {"amount": "750.00", "year_month": "2026-01"}


def _engine(tmp_path: Path, name: str) -> Engine:
    """Build an engine on a per-test SQLite file and create the schema.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Engine: An engine over the ``Base.metadata`` schema.
    """
    engine: Engine = create_db_engine(
        f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}"
    )
    Base.metadata.create_all(engine)
    return engine


def _session(tmp_path: Path, name: str) -> Session:
    """Return a Session bound to this test's own SQLite file.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Session: A fresh session over the created schema.
    """
    return create_session_factory(_engine(tmp_path, name))()


def _make_user(session: Session, email: str) -> User:
    """Persist and return a User with an opaque fake hash.

    Args:
        session: Session to write through (caller commits).
        email: Stored email value (unique per call site).

    Returns:
        User: The persisted model instance.
    """
    user = User(email=email, username=email.split("@")[0], hashed_password="x" * 60)
    session.add(user)
    session.commit()
    return user


class TestWriteAuditLog:
    """Writer contract coverage (t12 ac2)."""

    def test_create_row_has_null_old_value_and_new_value_with_exact_expense_payload_keys(
        self, tmp_path: Path
    ) -> None:
        """CREATE via keyword call: old NULL, new full, exact expense keys."""
        session = _session(
            tmp_path,
            "test_create_row_has_null_old_value_and_new_value_exact_expense",
        )
        with session:
            owner = _make_user(session, "audit-create@example.com")
            entity_id = uuid.uuid4()
            write_audit_log(
                db=session,
                user_id=owner.id,
                action="CREATE",
                entity_type="expense",
                entity_id=entity_id,
                old_value=None,
                new_value=dict(EXPENSE_PAYLOAD),
                ip_address="203.0.113.5",
            )
            session.commit()

        probe = _session(
            tmp_path,
            "test_create_row_has_null_old_value_and_new_value_exact_expense",
        )
        with probe:
            row = (
                probe.query(AuditLog)
                .filter(AuditLog.entity_id == entity_id)
                .one()
            )
            assert row.user_id == owner.id
            assert row.action == "CREATE"
            assert row.entity_type == "expense"
            assert row.old_value is None
            assert row.new_value == EXPENSE_PAYLOAD
            assert set(row.new_value) == {"amount", "date", "category_id", "note"}
            assert row.ip_address == "203.0.113.5"

    def test_update_row_has_both_values_with_exact_budget_payload_keys(
        self, tmp_path: Path
    ) -> None:
        """UPDATE: both payloads populated with exactly {amount, year_month}."""
        session = _session(
            tmp_path, "test_update_row_has_both_values_with_exact_budget_payload_keys"
        )
        with session:
            owner = _make_user(session, "audit-update@example.com")
            entity_id = uuid.uuid4()
            write_audit_log(
                db=session,
                user_id=owner.id,
                action="UPDATE",
                entity_type="budget",
                entity_id=entity_id,
                old_value=dict(BUDGET_PAYLOAD_OLD),
                new_value=dict(BUDGET_PAYLOAD),
                ip_address="198.51.100.7",
            )
            session.commit()

        probe = _session(
            tmp_path, "test_update_row_has_both_values_with_exact_budget_payload_keys"
        )
        with probe:
            row = (
                probe.query(AuditLog)
                .filter(AuditLog.entity_id == entity_id)
                .one()
            )
            assert row.action == "UPDATE"
            assert row.entity_type == "budget"
            assert row.old_value == BUDGET_PAYLOAD_OLD
            assert row.new_value == BUDGET_PAYLOAD
            assert set(row.old_value) == {"amount", "year_month"}
            assert set(row.new_value) == {"amount", "year_month"}
            assert row.ip_address == "198.51.100.7"

    def test_delete_row_has_old_value_and_null_new_value(self, tmp_path: Path) -> None:
        """DELETE: old_value full (expense keys), new_value NULL."""
        session = _session(tmp_path, "test_delete_row_has_old_value_and_null_new_value")
        with session:
            owner = _make_user(session, "audit-delete@example.com")
            entity_id = uuid.uuid4()
            write_audit_log(
                db=session,
                user_id=owner.id,
                action="DELETE",
                entity_type="expense",
                entity_id=entity_id,
                old_value=dict(EXPENSE_PAYLOAD),
                new_value=None,
                ip_address=None,
            )
            session.commit()

        probe = _session(tmp_path, "test_delete_row_has_old_value_and_null_new_value")
        with probe:
            row = (
                probe.query(AuditLog)
                .filter(AuditLog.entity_id == entity_id)
                .one()
            )
            assert row.action == "DELETE"
            assert row.old_value == EXPENSE_PAYLOAD
            assert row.new_value is None
            assert row.ip_address is None

    def test_logger_never_commits_row_visible_only_after_caller_commit(
        self, tmp_path: Path
    ) -> None:
        """Second-session probe: flush alone keeps the row invisible."""
        name = "test_logger_never_commits_row_visible_only_after_caller_commit"
        engine = _engine(tmp_path, name)
        factory = create_session_factory(engine)
        session = factory()
        owner = _make_user(session, "audit-nocommit@example.com")
        entity_id = uuid.uuid4()

        write_audit_log(
            db=session,
            user_id=owner.id,
            action="CREATE",
            entity_type="expense",
            entity_id=entity_id,
            old_value=None,
            new_value=dict(EXPENSE_PAYLOAD),
            ip_address="203.0.113.5",
        )
        session.flush()

        # A second session over the same engine must NOT see the row:
        # the logger staged it in the caller's uncommitted transaction.
        probe = factory()
        assert (
            probe.query(AuditLog).filter(AuditLog.entity_id == entity_id).first()
            is None
        )

        session.commit()
        assert (
            probe.query(AuditLog).filter(AuditLog.entity_id == entity_id).first()
            is not None
        )

        # The rollback branch: a rolled-back write leaves zero rows.
        rollback_entity = uuid.uuid4()
        write_audit_log(
            db=session,
            user_id=owner.id,
            action="CREATE",
            entity_type="expense",
            entity_id=rollback_entity,
            old_value=None,
            new_value=dict(EXPENSE_PAYLOAD),
            ip_address=None,
        )
        session.rollback()
        assert (
            probe.query(AuditLog)
            .filter(AuditLog.entity_id == rollback_entity)
            .first()
            is None
        )
        session.close()
        probe.close()
        engine.dispose()

    def test_get_audit_logger_returns_write_audit_log(self) -> None:
        """REQ-ARCH-022: zero-arg dependency returns the writer itself."""
        assert get_audit_logger() is write_audit_log


class TestAuditAtomicity:
    """Same-transaction atomicity proof (t12 ac3, review_plan W7)."""

    def test_action_check_violation_rolls_back_the_business_write(
        self, tmp_path: Path
    ) -> None:
        """Invalid action 'PATCH' fails in-transaction and kills the business row."""
        session = _session(
            tmp_path, "test_action_check_violation_rolls_back_the_business_write"
        )
        with session:
            owner = _make_user(session, "audit-atomic@example.com")
            owner_id = owner.id
            business = Category(
                name="Atomic Business Cat", color="#22C55E", user_id=owner_id
            )
            session.add(business)
            session.flush()  # same transaction; assigns the Python UUID PK
            business_id = business.id
            write_audit_log(
                db=session,
                user_id=owner_id,
                action="PATCH",  # pinned injection: violates ck_audit_action
                entity_type="expense",
                entity_id=uuid.uuid4(),
                old_value=None,
                new_value=dict(EXPENSE_PAYLOAD),
                ip_address="203.0.113.5",
            )
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()

        # Fresh session: NEITHER the business row NOR any audit row exists.
        probe = _session(
            tmp_path, "test_action_check_violation_rolls_back_the_business_write"
        )
        with probe:
            assert probe.get(Category, business_id) is None
            assert probe.query(AuditLog).count() == 0


class TestNoAuditApiSurface:
    """FR-AUD-2 absence check (t12 ac4, t11 openapi precedent)."""

    def test_openapi_has_no_path_containing_audit(self) -> None:
        """No endpoint ever exposes audit logs: no path contains 'audit'."""
        paths = app.openapi()["paths"]
        audit_paths = [p for p in paths if "audit" in p.lower()]
        assert audit_paths == []
        # non-vacuous sanity: the check inspects a populated document.
        assert len(paths) >= 5, paths
