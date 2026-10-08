"""Unit tests for the Expense model (t13 ac1, REQ-DB-030..034).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

Isolation follows the merged t10/t12 unit pattern (there is no
conftest.py): one private SQLite file PER TEST under ``tmp_path`` named
after the test, schema via ``Base.metadata.create_all`` (NOT alembic;
the migration itself is proven in tests/integration/
test_expense_migration.py). ``create_db_engine`` turns on
``PRAGMA foreign_keys`` so FK CASCADE/RESTRICT semantics are provable on
SQLite.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.schema import Table

from app.database import create_db_engine
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import Base, User

EXPECTED_COLUMNS = {
    "id",
    "user_id",
    "category_id",
    "amount",
    "currency",
    "date",
    "note",
    "created_at",
    "updated_at",
}


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


def _seed_user_and_category(session: Session) -> tuple[User, Category]:
    """Persist one user and one custom category owned by them.

    Args:
        session: Active session.

    Returns:
        tuple[User, Category]: The persisted rows.
    """
    user = User(email="alice@example.com", username="alice", hashed_password="x")
    session.add(user)
    session.commit()
    category = Category(name="Groceries", color="#112233", user_id=user.id)
    session.add(category)
    session.commit()
    return user, category


def _make_expense(user: User, category: Category, **overrides: object) -> Expense:
    """Build an Expense row with contract defaults and overrides.

    Args:
        user: Owner row.
        category: Category row.
        **overrides: Column overrides applied to the new instance.

    Returns:
        Expense: An unsaved instance.
    """
    values: dict[str, object] = {
        "user_id": user.id,
        "category_id": category.id,
        "amount": Decimal("125.50"),
        "currency": "USD",
        "date": date(2026, 1, 15),
        "note": "weekly shop",
    }
    values.update(overrides)
    return Expense(**values)


class TestExpenseModel:
    """Contract coverage for the Expense model (t13 ac1)."""

    def test_columns_types_python_uuid_pk_and_fk_cascade_restrict_semantics(
        self, tmp_path: Path
    ) -> None:
        """Mapped shape matches REQ-DB-030 and FK actions are exact."""
        table = Expense.__table__
        assert isinstance(table, Table)
        assert table.name == "expenses"
        assert set(table.columns.keys()) == EXPECTED_COLUMNS
        # t13 precedent (t10/t12): Expense registers on the shared Base,
        # so assert the intent-preserving superset, not equality.
        assert {"users", "categories", "audit_logs", "expenses"} <= set(
            Base.metadata.tables
        )

        id_col = table.columns["id"]
        assert id_col.primary_key is True
        assert id_col.server_default is None  # UUIDs come from Python

        amount_type = table.columns["amount"].type
        assert amount_type.precision == 12 and amount_type.scale == 2
        assert table.columns["amount"].nullable is False
        assert table.columns["currency"].type.length == 3
        assert table.columns["currency"].default.arg == "USD"
        assert table.columns["note"].nullable is True

        fk_actions = {
            str(fk.target_fullname): str(fk.ondelete) for fk in table.foreign_keys
        }
        assert fk_actions["users.id"] == "CASCADE"
        assert fk_actions["categories.id"] == "RESTRICT"

        index_names = {index.name for index in table.indexes}
        assert {
            "idx_expenses_user_id",
            "idx_expenses_user_date",
            "idx_expenses_user_category",
            "idx_expenses_category_id",
        } == index_names

        # Live FK CASCADE probe: deleting the user removes their rows.
        session = _session(tmp_path, "test_columns_types_python_uuid_pk_fk")
        with session:
            user, category = _seed_user_and_category(session)
            expense = _make_expense(user, category)
            session.add(expense)
            session.commit()
            expense_id = expense.id
            session.delete(user)
            session.commit()
            remaining = int(
                session.scalar(
                    select(func.count()).select_from(Expense).where(
                        Expense.id == expense_id
                    )
                )
                or 0
            )
            assert remaining == 0  # user_id FK cascades

    def test_named_amount_and_currency_checks_reject_bad_values_on_sqlite(
        self, tmp_path: Path
    ) -> None:
        """ck_expenses_amount_positive / ck_expenses_currency_usd bite."""
        session = _session(tmp_path, "test_named_amount_and_currency_checks")
        with session:
            user, category = _seed_user_and_category(session)

            with pytest.raises(IntegrityError):
                session.add(_make_expense(user, category, amount=Decimal("0.00")))
                session.commit()
            session.rollback()

            with pytest.raises(IntegrityError):
                session.add(_make_expense(user, category, amount=Decimal("-1.00")))
                session.commit()
            session.rollback()

            with pytest.raises(IntegrityError):
                session.add(_make_expense(user, category, currency="EUR"))
                session.commit()
            session.rollback()

            # positive control: a valid row lands, defaulting currency
            good = _make_expense(user, category, currency="USD")
            session.add(good)
            session.commit()
            assert good.currency == "USD"
            assert int(
                session.scalar(select(func.count()).select_from(Expense)) or 0
            ) == 1

    def test_amount_roundtrips_as_decimal_with_exact_two_dp_equality(
        self, tmp_path: Path
    ) -> None:
        """Decimal("125.50") survives a SQLite round-trip exactly (REQ-DB-091)."""
        session = _session(tmp_path, "test_amount_roundtrips_as_decimal")
        with session:
            user, category = _seed_user_and_category(session)
            session.add(_make_expense(user, category, amount=Decimal("125.50")))
            session.commit()

            stored = session.scalars(select(Expense)).one()
            assert isinstance(stored.amount, Decimal)
            assert stored.amount.quantize(Decimal("0.01")) == Decimal("125.50")

    def test_date_is_timezone_naive_and_note_is_nullable(self, tmp_path: Path) -> None:
        """`date` is a plain Date column; note may be NULL (REQ-SEC-051)."""
        table = Expense.__table__
        assert not getattr(table.columns["date"].type, "timezone", False)
        assert type(table.columns["date"].type).__name__ == "Date"

        session = _session(tmp_path, "test_date_is_timezone_naive_note_nullable")
        with session:
            user, category = _seed_user_and_category(session)
            session.add(_make_expense(user, category, note=None))
            session.commit()

            stored = session.scalars(select(Expense)).one()
            assert stored.date == date(2026, 1, 15)
            assert stored.note is None
            assert stored.created_at is not None and stored.created_at.tzinfo is None
