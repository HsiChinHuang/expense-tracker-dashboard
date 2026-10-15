"""Unit tests for the demo-account seed (t65 ac3/ac4/ac5).

Class and function names are part of the issue contract: the AC
verification commands in docs/issues/t65.md reference these exact
pytest node IDs.

Isolation contract (t10 precedent): one SQLite file PER TEST under
``tmp_path``, named after the test; reading ``os.environ["DATABASE_URL"]``
is forbidden. ``create_all()`` is acceptable in unit modules. Every
test pins its own anchor so the dataset is reproducible regardless of
the wall clock.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.database import create_db_engine, create_session_factory
from app.models import Base
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User
from app.scripts.seed import SYSTEM_CATEGORIES
from app.scripts.seed_demo import (
    DEMO_EMAIL,
    SPAN_DAYS,
    seed_demo_data,
)

ANCHOR = date(2026, 10, 15)
"""Fixed anchor used by every test so generation never reads the clock."""


def _session(tmp_path: Path, name: str) -> Session:
    """Return a Session over this test's own SQLite file and schema.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Session: A fresh session with the full schema created.
    """
    engine: Engine = create_db_engine(
        f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}"
    )
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = create_session_factory(engine)
    return factory()


def _demo_id(session: Session) -> uuid.UUID:
    """Return the single demo account id.

    Args:
        session: Session over a seeded database.

    Returns:
        uuid.UUID: The demo user's primary key.
    """
    return session.execute(
        select(User.id).where(User.email == DEMO_EMAIL)
    ).scalar_one()


def _demo_expenses(session: Session) -> list[tuple[date, Decimal, str]]:
    """Return the demo rows as (date, amount, category_name) tuples.

    Money and date are read through the declared ORM types (Numeric /
    Date), never raw SQLite affinity, so the 2-dp Decimal assertions
    are meaningful.

    Args:
        session: Session over a seeded database.

    Returns:
        list[tuple[date, Decimal, str]]: One tuple per demo expense.
    """
    rows = session.execute(
        select(Expense.date, Expense.amount, Category.name)
        .join(Category, Category.id == Expense.category_id)
        .where(Expense.user_id == _demo_id(session))
    ).all()
    return [(r[0], r[1], r[2]) for r in rows]


class TestSeedDemoShape:
    """Contract coverage for the demo dataset shape (t65 ac3)."""

    def test_dataset_spans_ninety_days_and_covers_ten_system_categories_and_monthly_budgets(
        self, tmp_path: Path
    ) -> None:
        """90 consecutive days to the anchor, all ten categories, one budget per month."""
        session = _session(
            tmp_path,
            "test_dataset_spans_ninety_days_and_covers_ten_system_categories"
            "_and_monthly_budgets",
        )
        with session:
            seed_demo_data(session.connection(), anchor=ANCHOR)
            session.commit()
            rows = _demo_expenses(session)
            days = sorted({r[0] for r in rows})
            assert days[0] == ANCHOR - timedelta(days=SPAN_DAYS - 1)
            assert days[-1] == ANCHOR
            assert len(days) == SPAN_DAYS
            for _, amount, _ in rows:
                assert isinstance(amount, Decimal)
                assert amount > 0
                assert amount == amount.quantize(Decimal("0.01"))
                assert len(str(amount).split(".")[1]) == 2
            assert {r[2] for r in rows} == {
                entry["name"] for entry in SYSTEM_CATEGORIES
            }
            budgets = session.execute(
                select(Budget.year_month, Budget.amount).where(
                    Budget.user_id == _demo_id(session)
                )
            ).all()
            months = sorted({f"{d.year:04d}-{d.month:02d}" for d in days})
            assert sorted(b[0] for b in budgets) == months
            for _, value in budgets:
                assert isinstance(value, Decimal)
                assert value > 0
                assert len(str(value).split(".")[1]) == 2
        session.close()


class TestSeedDemoIdempotency:
    """Contract coverage for the wipe-and-rebuild idempotency (t65 ac4)."""

    def test_rerunning_wipes_and_rebuilds_the_demo_dataset_without_duplicates(
        self, tmp_path: Path
    ) -> None:
        """Three runs leave exactly one demo account and one copy of the data."""

        def snapshot(session: Session) -> tuple[object, ...]:
            """Return the (users, expenses, budgets, payload) snapshot.

            Args:
                session: Session over a seeded database.

            Returns:
                tuple[object, ...]: Counts plus the full demo payload
                    as sorted string tuples, so any drift is visible.
            """
            demo = _demo_id(session)
            expenses = session.execute(
                select(Expense.date, Expense.amount, Expense.note)
                .where(Expense.user_id == demo)
                .order_by(Expense.date, Expense.note, Expense.amount)
            ).all()
            budgets = session.execute(
                select(Budget.year_month, Budget.amount)
                .where(Budget.user_id == demo)
                .order_by(Budget.year_month)
            ).all()
            users = session.execute(select(func.count()).select_from(User)).scalar_one()
            payload = (
                [(str(r[0]), str(r[1]), str(r[2])) for r in expenses],
                [(b[0], str(b[1])) for b in budgets],
            )
            duplicates = len(expenses) - len(
                {(str(r[0]), str(r[2]), str(r[1])) for r in expenses}
            )
            return (users, len(expenses), len(budgets), payload, duplicates)

        session = _session(
            tmp_path,
            "test_rerunning_wipes_and_rebuilds_the_demo_dataset_without_duplicates",
        )
        with session:
            seed_demo_data(session.connection(), anchor=ANCHOR)
            session.commit()
            first = snapshot(session)
            seed_demo_data(session.connection(), anchor=ANCHOR)
            session.commit()
            second = snapshot(session)
            seed_demo_data(session.connection(), anchor=ANCHOR)
            session.commit()
            third = snapshot(session)
        session.close()
        assert first[0] == second[0] == third[0] == 1
        assert first[1] == second[1] == third[1]
        assert first[2] == second[2] == third[2]
        assert first[3] == second[3] == third[3]
        assert first[4] == second[4] == third[4] == 0


class TestSeedDemoIsolation:
    """Contract coverage for non-demo isolation (t65 ac5)."""

    def test_seeding_touches_no_non_demo_rows(self, tmp_path: Path) -> None:
        """A pre-existing other user's rows are byte-identical across a reseed."""
        session = _session(tmp_path, "test_seeding_touches_no_non_demo_rows")
        other = User(
            id=uuid.uuid4(),
            email="other.t65@example.com",
            username="othert65",
            hashed_password="not-a-real-hash-just-a-fixture-x",
            is_active=True,
        )
        session.add(other)
        session.flush()
        other_category = Category(
            id=uuid.uuid4(),
            user_id=other.id,
            name="Other",
            color="#112233",
            icon="star",
            is_system=False,
        )
        session.add(other_category)
        session.flush()
        session.add(
            Expense(
                id=uuid.uuid4(),
                user_id=other.id,
                category_id=other_category.id,
                amount=Decimal("12.34"),
                currency="USD",
                date=date(2026, 5, 1),
                note="other-user row that must survive",
            )
        )
        session.add(
            Budget(
                id=uuid.uuid4(),
                user_id=other.id,
                year_month="2026-05",
                amount=Decimal("100.00"),
            )
        )
        session.commit()

        def fingerprint() -> tuple[object, ...]:
            """Return the non-demo fingerprint (hash, counts, shared total).

            Returns:
                tuple[object, ...]: The other user's hash, their row
                    counts, the total expense count and the shared
                    system-category count.
            """
            stored_hash = session.execute(
                select(User.hashed_password).where(User.email == "other.t65@example.com")
            ).scalar_one()
            other_expenses = session.execute(
                select(func.count()).select_from(Expense).where(
                    Expense.user_id == other.id
                )
            ).scalar_one()
            other_budgets = session.execute(
                select(func.count()).select_from(Budget).where(
                    Budget.user_id == other.id
                )
            ).scalar_one()
            other_categories = session.execute(
                select(func.count()).select_from(Category).where(
                    Category.user_id == other.id
                )
            ).scalar_one()
            shared = session.execute(
                select(func.count()).select_from(Category).where(
                    Category.user_id.is_(None)
                )
            ).scalar_one()
            return (
                stored_hash,
                other_expenses,
                other_budgets,
                other_categories,
                shared,
            )

        before = fingerprint()
        # create_all seeds no categories here (the fence's alembic leg does),
        # so the pre-seed shared count is 0; the seed must establish the ten.
        assert before == ("not-a-real-hash-just-a-fixture-x", 1, 1, 1, 0)
        with session:
            seed_demo_data(session.connection(), anchor=ANCHOR)
            session.commit()
        after = fingerprint()
        assert after == before[:4] + (10,)
        demo_rows = session.execute(
            select(func.count()).select_from(Expense).where(
                Expense.user_id == _demo_id(session)
            )
        ).scalar_one()
        assert demo_rows >= SPAN_DAYS
        users = session.execute(select(func.count()).select_from(User)).scalar_one()
        assert users == 2
        session.close()
