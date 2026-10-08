"""Unit tests for the Category model (t10 ac1).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation contract (docs/issues/t10.md): every test builds its OWN
SQLite file under pytest's ``tmp_path`` named after the test itself.
Reading ``os.environ["DATABASE_URL"]`` (t6's helper) is forbidden here
because ac1 runs six nodes inside ONE pytest process and a shared file
makes them collide on the previous test's rows. ``create_all()`` is
allowed in the unit modules per the t6/t8 precedent; the migration's
own DDL is covered by tests/integration/test_category_migration.py.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy import Engine, String, Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import create_db_engine, create_session_factory
from app.models import Category, User
from app.models.user import Base

EXPECTED_COLUMNS = {
    "id",
    "user_id",
    "name",
    "color",
    "icon",
    "is_system",
    "created_at",
}


def _engine(tmp_path: Path, name: str) -> Engine:
    """Build an engine on a per-test SQLite file and create the schema.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Engine: An engine whose database holds the ``Base.metadata``
            schema (users + categories as the model defines it).
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


def _make_user(email: str) -> User:
    """Build an unsaved User with an opaque fake hash.

    Args:
        email: Stored email value (unique per call site).

    Returns:
        User: A transient model instance.
    """
    return User(email=email, username=email.split("@")[0], hashed_password="x" * 60)


class TestCategoryModel:
    """Contract coverage for the Category model (t10 ac1)."""

    def test_system_and_custom_rows_persist_with_python_uuid_and_typed_columns(
        self, tmp_path: Path
    ) -> None:
        """Mapped shape matches REQ-DB-020 and both row shapes round-trip."""
        table = cast(Table, Category.__table__)

        assert table.name == "categories"
        assert set(table.columns.keys()) == EXPECTED_COLUMNS
        # t12 amendment (t10 precedent): AuditLog registers on the shared
        # Base, so assert the intent-preserving superset, not equality.
        assert {"users", "categories"} <= set(Base.metadata.tables)

        id_col = table.columns["id"]
        user_id_col = table.columns["user_id"]
        name_col = table.columns["name"]
        color_col = table.columns["color"]
        icon_col = table.columns["icon"]
        is_system_col = table.columns["is_system"]
        created_col = table.columns["created_at"]

        assert id_col.primary_key is True
        assert id_col.server_default is None  # UUIDs come from Python
        assert user_id_col.nullable is True
        assert cast(String, name_col.type).length == 100
        assert name_col.nullable is False
        assert cast(String, color_col.type).length == 7
        assert color_col.nullable is False
        assert cast(String, icon_col.type).length == 50
        assert icon_col.nullable is True
        assert is_system_col.nullable is False
        assert created_col.nullable is False
        assert created_col.server_default is not None

        fks = list(table.foreign_keys)
        assert len(fks) == 1
        assert fks[0].target_fullname == "users.id"
        assert fks[0].ondelete == "CASCADE"

        checks = {
            cast(str, c.name)
            for c in table.constraints
            if c.__class__.__name__ == "CheckConstraint"
        }
        assert {
            "ck_categories_color_format",
            "ck_categories_system_consistency",
        } <= checks

        session = _session(
            tmp_path,
            "test_system_and_custom_rows_persist_with_python_uuid_and_typed_columns",
        )
        with session:
            owner = _make_user("category-owner@example.com")
            session.add(owner)
            session.commit()

            system_row = Category(
                name="Food & Dining",
                color="#EF4444",
                icon="utensils",
                is_system=True,
            )
            custom_row = Category(
                name="My Fun Stuff", color="#abcdef", user_id=owner.id
            )
            session.add_all([system_row, custom_row])
            session.commit()
            session.refresh(system_row)
            session.refresh(custom_row)

            assert isinstance(system_row.id, uuid.UUID)
            assert isinstance(custom_row.id, uuid.UUID)
            assert system_row.user_id is None
            assert system_row.is_system is True
            assert custom_row.user_id == owner.id
            assert custom_row.is_system is False
            assert custom_row.icon is None
            assert isinstance(system_row.created_at, datetime)
            assert isinstance(custom_row.created_at, datetime)

    @pytest.mark.parametrize(
        ("bad_color"),
        ["EF4444", "#GGGGGG", "#12345", "#1234567"],
    )
    def test_invalid_hex_color_raises_integrity_error(
        self, tmp_path: Path, bad_color: str
    ) -> None:
        """Each invalid HEX color is rejected by ck_categories_color_format."""
        session = _session(tmp_path, f"test_invalid_hex_color_{bad_color}")
        with session, pytest.raises(IntegrityError):
            session.add(Category(name="Bad color", color=bad_color, is_system=True))
            session.commit()

    def test_system_row_with_user_id_and_custom_row_without_user_id_raise_integrity_error(
        self, tmp_path: Path
    ) -> None:
        """Both mismatched shapes violate ck_categories_system_consistency."""
        session = _session(
            tmp_path,
            "test_system_row_with_user_id_and_custom_row_without_user_id",
        )
        with session:
            owner = _make_user("consistency-owner@example.com")
            session.add(owner)
            session.commit()
            owner_id = owner.id

        with session, pytest.raises(IntegrityError):
            session.add(
                Category(
                    name="System but owned",
                    color="#22C55E",
                    is_system=True,
                    user_id=owner_id,
                )
            )
            session.commit()
        session.rollback()

        with session, pytest.raises(IntegrityError):
            session.add(
                Category(name="Custom but unowned", color="#3B82F6", is_system=False)
            )
            session.commit()
