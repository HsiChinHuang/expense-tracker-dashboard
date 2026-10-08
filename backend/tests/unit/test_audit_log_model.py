"""Unit tests for the AuditLog model (t12 ac1).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation contract (docs/issues/t12.md): every test builds its OWN
SQLite file under pytest's ``tmp_path`` named after the test itself
(COPY of the tests/unit/test_category_model.py harness; there is no
conftest.py). ``create_all()`` is allowed in the unit modules per the
t6/t8/t10 precedent; the migration's own DDL is covered by
tests/integration/test_audit_migration.py.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pytest
from sqlalchemy import Engine, String, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import create_db_engine, create_session_factory
from app.models import AuditLog, Base, User

EXPECTED_COLUMNS = {
    "id",
    "user_id",
    "action",
    "entity_type",
    "entity_id",
    "old_value",
    "new_value",
    "ip_address",
    "created_at",
}


def _engine(tmp_path: Path, name: str) -> Engine:
    """Build an engine on a per-test SQLite file and create the schema.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Engine: An engine whose database holds the ``Base.metadata``
            schema (users + categories + audit_logs as the models define).
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


def _audit_row(user_id: uuid.UUID, **overrides: Any) -> AuditLog:
    """Build an AuditLog with valid defaults overridable per test.

    Args:
        user_id: Owning user's id (audit_logs.user_id is NOT NULL).
        overrides: Column values replacing the defaults.

    Returns:
        AuditLog: A transient model instance.
    """
    defaults: dict[str, Any] = {
        "user_id": user_id,
        "action": "CREATE",
        "entity_type": "expense",
        "entity_id": uuid.uuid4(),
    }
    defaults.update(overrides)
    return AuditLog(**defaults)


class TestAuditLogModel:
    """Contract coverage for the AuditLog model (t12 ac1)."""

    def test_columns_nullability_python_uuid_pk_and_no_cascade_fk(
        self, tmp_path: Path
    ) -> None:
        """Mapped shape matches REQ-DB-050 incl. the preserve-on-delete FK."""
        table = cast(Table, AuditLog.__table__)

        assert table.name == "audit_logs"
        assert set(table.columns.keys()) == EXPECTED_COLUMNS
        assert {"users", "categories", "audit_logs"} <= set(Base.metadata.tables)

        id_col = table.columns["id"]
        user_id_col = table.columns["user_id"]
        action_col = table.columns["action"]
        entity_type_col = table.columns["entity_type"]
        entity_id_col = table.columns["entity_id"]
        old_col = table.columns["old_value"]
        new_col = table.columns["new_value"]
        ip_col = table.columns["ip_address"]
        created_col = table.columns["created_at"]

        assert id_col.primary_key is True
        assert id_col.server_default is None  # UUIDs come from Python (REQ-TECH-032)
        assert user_id_col.nullable is False
        assert cast(String, action_col.type).length == 10
        assert action_col.nullable is False
        assert cast(String, entity_type_col.type).length == 20
        assert entity_type_col.nullable is False
        assert entity_id_col.nullable is False  # review_plan W5
        assert old_col.nullable is True
        assert new_col.nullable is True
        assert cast(String, ip_col.type).length == 45
        assert ip_col.nullable is True
        assert created_col.nullable is False
        assert created_col.server_default is not None

        # Exactly one FK (user_id -> users.id) with NO ondelete cascade
        # (Chapter 6 6.11.2 preserve-on-user-delete) and none on entity_id.
        fks = list(table.foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "users.id"
        assert fks[0].parent.name == "user_id"
        assert fks[0].ondelete is None

        checks = {
            cast(str, c.name)
            for c in table.constraints
            if c.__class__.__name__ == "CheckConstraint"
        }
        assert {"ck_audit_action", "ck_audit_entity_type"} <= checks

        indexes = {cast(str, i.name) for i in table.indexes}
        assert {
            "idx_audit_user_created",
            "idx_audit_entity",
            "idx_audit_action",
        } <= indexes

        session = _session(
            tmp_path,
            "test_columns_nullability_python_uuid_pk_and_no_cascade_fk",
        )
        with session:
            owner = _make_user(session, "audit-shape@example.com")
            row = _audit_row(owner.id)
            session.add(row)
            session.commit()
            session.refresh(row)
            assert isinstance(row.id, uuid.UUID)
            assert isinstance(row.created_at, datetime)
            assert row.old_value is None
            assert row.new_value is None
            assert row.ip_address is None

    def test_entity_id_is_required(self, tmp_path: Path) -> None:
        """INSERT without entity_id violates the NOT NULL pin (W5)."""
        session = _session(tmp_path, "test_entity_id_is_required")
        with session:
            owner = _make_user(session, "audit-entity-id@example.com")
            owner_id = owner.id
        with session, pytest.raises(IntegrityError):
            session.add(_audit_row(owner_id, entity_id=None))
            session.commit()

    def test_action_and_entity_type_checks_reject_out_of_set_values(
        self, tmp_path: Path
    ) -> None:
        """ck_audit_action and ck_audit_entity_type reject out-of-set rows."""
        session = _session(
            tmp_path, "test_action_and_entity_type_checks_reject_out_of_set_values"
        )
        with session:
            owner = _make_user(session, "audit-checks@example.com")
            owner_id = owner.id

        with session, pytest.raises(IntegrityError):
            session.add(_audit_row(owner_id, action="PATCH"))
            session.commit()
        session.rollback()

        with session, pytest.raises(IntegrityError):
            # 'category' is deliberately NOT auditable (REQ-DB-051).
            session.add(_audit_row(owner_id, entity_type="category"))
            session.commit()
        session.rollback()

        with session:
            assert session.query(AuditLog).count() == 0

    def test_json_variant_payload_roundtrips_and_old_new_are_independently_nullable(
        self, tmp_path: Path
    ) -> None:
        """REQ-DB-054: dict payloads round-trip on SQLite TEXT; old/new free."""
        session = _session(
            tmp_path,
            "test_json_variant_payload_roundtrips_and_old_new_independent",
        )
        with session:
            owner = _make_user(session, "audit-json@example.com")
            owner_id = owner.id
            entity = uuid.uuid4()
            old_payload: dict[str, Any] = {"amount": "10.00", "year_month": "2026-01"}
            new_payload: dict[str, Any] = {"amount": "125.50", "year_month": "2026-01"}

            both = _audit_row(
                owner_id,
                action="UPDATE",
                entity_type="budget",
                entity_id=entity,
                old_value=old_payload,
                new_value=new_payload,
                ip_address="203.0.113.5",
            )
            create_only = _audit_row(
                owner_id,
                action="CREATE",
                entity_type="budget",
                old_value=None,
                new_value=new_payload,
            )
            delete_only = _audit_row(
                owner_id,
                action="DELETE",
                entity_type="budget",
                old_value=old_payload,
                new_value=None,
            )
            session.add_all([both, create_only, delete_only])
            session.commit()
            ids = (both.id, create_only.id, delete_only.id)

        # Read the persisted CONTENT back through a FRESH session.
        # Same SQLite file, brand-new Session (fresh identity map).
        probe = _session(
            tmp_path,
            "test_json_variant_payload_roundtrips_and_old_new_independent",
        )
        with probe:
            rows = {row.id: row for row in probe.query(AuditLog).all()}
            assert rows[ids[0]].old_value == old_payload
            assert rows[ids[0]].new_value == new_payload
            assert rows[ids[0]].ip_address == "203.0.113.5"
            assert rows[ids[1]].old_value is None
            assert rows[ids[1]].new_value == new_payload
            assert rows[ids[2]].old_value == old_payload
            assert rows[ids[2]].new_value is None
