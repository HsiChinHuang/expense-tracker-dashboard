"""Unit tests for the Budget model (t14 ac1, REQ-DB-040..042).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation follows the merged t10/t12/t13 unit pattern (there is no
conftest.py): one private SQLite file PER TEST under ``tmp_path`` named
after the test, schema via ``Base.metadata.create_all`` (NOT alembic;
the migration itself is proven in tests/integration/
test_budget_migration.py). ``create_db_engine`` turns on
``PRAGMA foreign_keys`` so FK CASCADE semantics are provable on SQLite.

Per review_plan W9 the UNIQUE proof is a STATIC constraint guard: two
SEQUENTIAL raw inserts for the same (user, month) in one session raise
IntegrityError. This is NOT a concurrency test and no retry/race/
ON CONFLICT machinery exists anywhere here (REQ-PROD-035 is phase_5).
"""

import uuid
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.schema import Table

from app.database import create_db_engine
from app.models.budget import Budget
from app.models.user import Base, User

EXPECTED_COLUMNS = {"id", "user_id", "year_month", "amount", "created_at", "updated_at"}


def _session(tmp_path: Path, name: str) -> Session:
    """Return a Session over this test's own SQLite file and schema.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Session: A fresh session with the full Base metadata created.
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = sessionmaker(bind=engine, expire_on_commit=False)
    return factory()


def _seed_user(session: Session) -> User:
    """Persist one user and return it.

    Args:
        session: Active session.

    Returns:
        User: The persisted row.
    """
    user = User(email="alice@example.com", username="alice", hashed_password="x")
    session.add(user)
    session.commit()
    return user


def _make_budget(user: User, **overrides: object) -> Budget:
    """Build a Budget row with contract defaults and overrides.

    Args:
        user: Owner row.
        **overrides: Column overrides applied to the new instance.

    Returns:
        Budget: An unsaved instance.
    """
    values: dict[str, object] = {
        "user_id": user.id,
        "year_month": "2026-10",
        "amount": Decimal("2000.00"),
    }
    values.update(overrides)
    return Budget(**values)


class TestBudgetModel:
    """Contract coverage for the Budget model (t14 ac1)."""

    def test_columns_types_python_uuid_pk_and_cascade_fk_semantics(
        self, tmp_path: Path
    ) -> None:
        """Mapped shape matches REQ-DB-040 and the FK action is exact."""
        table = Budget.__table__
        assert isinstance(table, Table)
        assert table.name == "budgets"
        assert set(table.columns.keys()) == EXPECTED_COLUMNS
        # t13 precedent (t10/t12): Budget registers on the shared Base,
        # so assert the intent-preserving superset, not equality.
        assert {"users", "categories", "audit_logs", "expenses", "budgets"} <= set(
            Base.metadata.tables
        )

        id_col = table.columns["id"]
        assert id_col.primary_key is True
        assert id_col.server_default is None  # UUIDs come from Python
        assert id_col.default is not None and callable(id_col.default.arg)

        assert table.columns["user_id"].nullable is False
        assert table.columns["year_month"].nullable is False
        assert table.columns["year_month"].type.length == 7
        # year_month is a plain str key, never a date object (REQ-SEC-051)
        assert type(table.columns["year_month"].type).__name__ == "String"

        amount_type = table.columns["amount"].type
        assert amount_type.precision == 12 and amount_type.scale == 2
        assert table.columns["amount"].nullable is False

        assert not getattr(table.columns["created_at"].type, "timezone", False)
        assert table.columns["created_at"].server_default is not None
        assert table.columns["updated_at"].server_default is not None

        fk_actions = {str(fk.target_fullname): str(fk.ondelete) for fk in table.foreign_keys}
        assert fk_actions == {"users.id": "CASCADE"}

        constraint_names = {constraint.name for constraint in table.constraints if constraint.name}
        assert {
            "uq_budgets_user_month",
            "ck_budgets_amount_positive",
            "ck_budgets_year_month_format",
        } == constraint_names

        # Live FK CASCADE probe: deleting the user removes their budgets.
        session = _session(tmp_path, "test_columns_types_python_uuid_pk_cascade")
        with session:
            user = _seed_user(session)
            budget = _make_budget(user)
            session.add(budget)
            session.commit()
            budget_id = budget.id
            session.delete(user)
            session.commit()
            remaining = int(
                session.scalar(
                    select(func.count()).select_from(Budget).where(Budget.id == budget_id)
                )
                or 0
            )
            assert remaining == 0  # user_id FK cascades

    def test_named_unique_and_both_checks_reject_bad_values_on_sqlite(
        self, tmp_path: Path
    ) -> None:
        """uq_budgets_user_month / both CHECKs bite on SQLite."""
        session = _session(tmp_path, "test_named_unique_and_both_checks")
        with session:
            user = _seed_user(session)

            # ck_budgets_amount_positive
            with pytest.raises(IntegrityError):
                session.add(_make_budget(user, amount=Decimal("0.00")))
                session.commit()
            session.rollback()

            with pytest.raises(IntegrityError):
                session.add(_make_budget(user, amount=Decimal("-1.00")))
                session.commit()
            session.rollback()

            # ck_budgets_year_month_format (GLOB emulation, anchored)
            for bad_month in ("2026-1", "abcd-ef", "20261-3", "202613"):
                with pytest.raises(IntegrityError):
                    session.add(_make_budget(user, year_month=bad_month))
                    session.commit()
                session.rollback()

            # uq_budgets_user_month (static guard; W9 wording applies)
            session.add(_make_budget(user, year_month="2026-10"))
            session.commit()
            with pytest.raises(IntegrityError):
                session.add(_make_budget(user, year_month="2026-10", amount=Decimal("1.00")))
                session.commit()
            session.rollback()

            # 2026-13 passes the CHECK BY DESIGN (month-value is API-owned)
            session.add(_make_budget(user, year_month="2026-13"))
            session.commit()
            assert int(session.scalar(select(func.count()).select_from(Budget)) or 0) == 2

    def test_two_sequential_inserts_for_same_user_and_month_raise_integrity_error(
        self, tmp_path: Path
    ) -> None:
        """W9 static UNIQUE guard: two sequential raw inserts raise.

        This is the constraint proof behind the upsert contract, NOT a
        concurrency test (REQ-PROD-035's real scenario is phase_5 ops).
        """
        session = _session(tmp_path, "test_two_sequential_inserts_unique")
        with session:
            user = _seed_user(session)
            connection = session.connection()
            connection.execute(
                cast(Table, Budget.__table__).insert().values(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    year_month="2026-10",
                    amount=Decimal("100.00"),
                )
            )
            session.commit()  # first insert is durable
            # session.commit() released the previous connection; the
            # SECOND sequential raw insert re-acquires a live one.
            with pytest.raises(IntegrityError):
                session.connection().execute(
                    cast(Table, Budget.__table__).insert().values(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        year_month="2026-10",
                        amount=Decimal("250.00"),
                    )
                )
            session.rollback()

        with session:
            # the first row survived the failed second insert
            count = int(
                session.scalar(
                    select(func.count()).select_from(Budget).where(
                        Budget.year_month == "2026-10"
                    )
                )
                or 0
            )
            assert count == 1

    def test_amount_roundtrips_as_decimal_with_exact_two_dp_equality(
        self, tmp_path: Path
    ) -> None:
        """Decimal("2000.00") survives a SQLite round-trip exactly (REQ-DB-091)."""
        session = _session(tmp_path, "test_amount_roundtrips_as_decimal")
        with session:
            user = _seed_user(session)
            session.add(_make_budget(user, amount=Decimal("2000.00")))
            session.commit()

            stored = session.scalars(select(Budget)).one()
            assert isinstance(stored.amount, Decimal)
            assert stored.amount.quantize(Decimal("0.01")) == Decimal("2000.00")
            assert isinstance(stored.year_month, str)
            assert stored.year_month == "2026-10"
