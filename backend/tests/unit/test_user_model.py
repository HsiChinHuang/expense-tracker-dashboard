"""Unit tests for the User model and its DB-level behavior (t6).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs. The AC
commands inject a tmp-file SQLite URL through DATABASE_URL; when the
full suite runs without it, a per-test tmp_path file is used instead so
`backend/dev.db` is never touched. The schema is created from
``Base.metadata`` per test (mirroring what revision 001 provisions).
"""

import os
import time
import uuid
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy import String, Table
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.database import create_db_engine, create_session_factory
from app.models.user import Base, User

EXPECTED_COLUMNS = {
    "id",
    "email",
    "username",
    "hashed_password",
    "is_active",
    "created_at",
    "updated_at",
}


def _sqlite_url(tmp_path: Path) -> str:
    """Return the injected DATABASE_URL or a tmp-file fallback.

    Args:
        tmp_path: pytest-provided directory for the fallback file.

    Returns:
        str: A SQLite URL that never resolves to backend/dev.db.
    """
    injected = os.environ.get("DATABASE_URL")
    if injected:
        return injected
    return f"sqlite:///{(tmp_path / 't6_test.db').as_posix()}"


def _session(tmp_path: Path) -> Session:
    """Create the schema on a fresh engine and return a new Session.

    Args:
        tmp_path: pytest-provided directory for the fallback database.

    Returns:
        Session: A session bound to a database containing the users
            table as revision 001 defines it.
    """
    engine: Engine = create_db_engine(_sqlite_url(tmp_path))
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = create_session_factory(engine)
    return factory()


def _make_user(email: str, username: str) -> User:
    """Build an unsaved User with an opaque fake hash (t7 owns hashing).

    Args:
        email: Stored email value.
        username: Stored username value.

    Returns:
        User: A transient model instance.
    """
    return User(
        email=email,
        username=username,
        hashed_password="x" * 60,
    )


class TestUserModel:
    """Contract coverage for the User model (ac1, ac3, ac4)."""

    def test_creates_user_with_python_uuid_default_and_typed_columns(
        self, tmp_path: Path
    ) -> None:
        """Mapped shape matches REQ-DB-010 and inserts yield a UUID id."""
        table = cast(Table, User.__table__)

        assert table.name == "users"
        assert set(table.columns.keys()) == EXPECTED_COLUMNS
        tables = set(Base.metadata.tables)
        assert "users" in tables
        # t14 amendment (t12/t13 precedent): the budgets table
        # legitimately exists now (revision 005), so the not-yet-exists
        # guard has no remaining subject and retires to the vacuous-safe
        # superset check; every table's own issue owns its existence pin.
        assert {"users", "categories", "audit_logs", "expenses", "budgets"} <= tables

        email_col = table.columns["email"]
        username_col = table.columns["username"]
        password_col = table.columns["hashed_password"]
        assert email_col.unique is True
        assert email_col.index is True
        assert email_col.nullable is False
        assert cast(String, email_col.type).length == 255
        assert username_col.unique is True
        assert username_col.nullable is False
        assert cast(String, username_col.type).length == 50
        assert cast(String, password_col.type).length == 255
        assert table.columns["is_active"].nullable is False
        assert table.columns["id"].primary_key is True
        assert table.columns["id"].server_default is None

        session = _session(tmp_path)
        with session:
            user = _make_user("ac1@example.com", "ac1user")
            session.add(user)
            session.commit()
            session.refresh(user)

            assert isinstance(user.id, uuid.UUID)
            assert user.created_at is not None
            assert user.updated_at is not None

    def test_duplicate_email_raises_integrity_error(self, tmp_path: Path) -> None:
        """A second row with the same stored email fails at the DB."""
        session = _session(tmp_path)
        with session:
            session.add(_make_user("dup-email@example.com", "first-user"))
            session.commit()

        second = _session(tmp_path)
        with second, pytest.raises(IntegrityError):
            second.add(_make_user("dup-email@example.com", "second-user"))
            second.commit()

    def test_duplicate_username_raises_integrity_error(self, tmp_path: Path) -> None:
        """Username uniqueness is case-sensitive (SQLite BINARY collation).

        An exact-case duplicate username raises IntegrityError, while a
        different-case username ('same' then 'SAME') is accepted: that is
        what proves the comparison is byte-exact (a wrongly collated,
        NOCASE-style implementation would reject it and fail here).
        See the [AC SUGGESTION] in the t6 handoff: the AC's "different
        case MUST still be rejected" clause would prove the opposite
        (case-insensitivity), contradicting REQ-DB-011.
        """
        session = _session(tmp_path)
        with session:
            session.add(_make_user("case-a@example.com", "same"))
            session.commit()

        duplicate = _session(tmp_path)
        with duplicate, pytest.raises(IntegrityError):
            duplicate.add(_make_user("case-b@example.com", "same"))
            duplicate.commit()

        other_case = _session(tmp_path)
        with other_case:
            other_case.add(_make_user("case-c@example.com", "SAME"))
            other_case.commit()
            assert (
                other_case.query(User.id).filter(User.username == "SAME").count() == 1
            )

    def test_updated_at_refreshes_on_update(self, tmp_path: Path) -> None:
        """An ORM update refreshes updated_at via the onupdate clause."""
        session = _session(tmp_path)
        with session:
            user = _make_user("stamps@example.com", "stamps")
            session.add(user)
            session.commit()
            session.refresh(user)
            original_updated_at = user.updated_at
            assert user.updated_at >= user.created_at

            time.sleep(1.1)
            user.username = "stamps-renamed"
            session.commit()
            session.refresh(user)

            assert user.updated_at > original_updated_at
            assert user.updated_at >= user.created_at

    def test_is_active_defaults_true_on_insert(self, tmp_path: Path) -> None:
        """A row inserted without is_active reloads with is_active True."""
        session = _session(tmp_path)
        with session:
            user = _make_user("active@example.com", "active")
            assert "is_active" not in user.__dict__
            session.add(user)
            session.commit()
            user_id = user.id

        fresh = _session(tmp_path)
        with fresh:
            reloaded = fresh.get(User, user_id)

        assert reloaded is not None
        assert reloaded.is_active is True
