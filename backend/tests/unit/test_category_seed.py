"""Unit tests for the idempotent system-category seed (t10 ac3).

Class and function names are part of the issue contract. The seed is
called directly here — that is Chapter 5 section 5.9.3's "SQLite tests"
row (the migration-level trigger is covered by
tests/integration/test_category_migration.py::test_upgrade_head_seeds_exactly_ten_system_categories).

Isolation contract: one SQLite file PER TEST under ``tmp_path``, named
after the test; reading ``os.environ["DATABASE_URL"]`` is forbidden.
``create_all()`` is acceptable in the unit modules (t6/t8 precedent).
"""

import uuid
from pathlib import Path

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.database import create_db_engine, create_session_factory
from app.models import Base  # app.models registers users + categories
from app.scripts.seed import SYSTEM_CATEGORIES, seed_system_categories

# Chapter 5 section 5.9.1, verbatim — asserted against the module table.
PINNED_ROWS = [
    ("Food & Dining", "#EF4444", "utensils"),
    ("Groceries", "#F97316", "shopping-cart"),
    ("Transportation", "#EAB308", "car"),
    ("Housing & Rent", "#22C55E", "home"),
    ("Utilities", "#14B8A6", "zap"),
    ("Entertainment", "#3B82F6", "film"),
    ("Shopping", "#8B5CF6", "bag"),
    ("Health & Fitness", "#EC4899", "heart"),
    ("Travel", "#06B6D4", "plane"),
    ("Other", "#6B7280", "more-horizontal"),
]

_categories = Base.metadata.tables["categories"]


def _session(tmp_path: Path, name: str) -> Session:
    """Return a Session over this test's own SQLite file and schema.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Session: A fresh session with users + categories created.
    """
    engine: Engine = create_db_engine(
        f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}"
    )
    Base.metadata.create_all(engine)
    factory: sessionmaker[Session] = create_session_factory(engine)
    return factory()


def _seeded_rows(session: Session) -> list[tuple[str, str, str]]:
    """Return the seeded (name, color, icon) triples in insertion order.

    Args:
        session: Session over a database containing the categories table.

    Returns:
        list[tuple[str, str, str]]: Every user_id IS NULL row's content.
    """
    rows = session.execute(
        select(_categories.c.name, _categories.c.color, _categories.c.icon)
        .where(_categories.c.user_id.is_(None))
        .order_by(_categories.c.name)
    ).all()
    return [(str(r[0]), str(r[1]), str(r[2])) for r in rows]


class TestSeedCategories:
    """Contract coverage for seed_system_categories (t10 ac3)."""

    def test_seed_inserts_exactly_the_ten_pinned_system_rows(
        self, tmp_path: Path
    ) -> None:
        """The table and one seed run produce the ten section 5.9.1 rows."""
        assert [(r["name"], r["color"], r["icon"]) for r in SYSTEM_CATEGORIES] == PINNED_ROWS

        session = _session(
            tmp_path, "test_seed_inserts_exactly_the_ten_pinned_system_rows"
        )
        with session:
            inserted = seed_system_categories(session.connection())
            session.commit()

            assert inserted == 10
            counts = session.execute(
                select(_categories.c.is_system, _categories.c.user_id)
            ).all()
            assert len(counts) == 10
            assert all(bool(c[0]) and c[1] is None for c in counts)

            seeded = _seeded_rows(session)
            assert sorted(seeded) == sorted(PINNED_ROWS)

    def test_second_seed_run_inserts_nothing(self, tmp_path: Path) -> None:
        """Three consecutive runs insert 10, 0, 0 and leave ten rows."""
        session = _session(tmp_path, "test_second_seed_run_inserts_nothing")
        with session:
            first = seed_system_categories(session.connection())
            session.commit()
            second = seed_system_categories(session.connection())
            session.commit()
            third = seed_system_categories(session.connection())
            session.commit()

            assert (first, second, third) == (10, 0, 0)
            total = session.execute(select(_categories.c.id)).all()
            assert len(total) == 10

    def test_seed_ids_are_python_uuids_and_partial_index_still_holds(
        self, tmp_path: Path
    ) -> None:
        """Seed ids are distinct UUIDs and duplicate system names are kept."""
        session = _session(
            tmp_path, "test_seed_ids_are_python_uuids_and_partial_index_still_holds"
        )
        with session:
            seed_system_categories(session.connection())
            session.commit()

            ids = session.execute(select(_categories.c.id)).scalars().all()
            assert len(ids) == 10
            assert len(set(ids)) == 10
            assert all(isinstance(i, uuid.UUID) for i in ids)

            # The partial unique index excludes user_id IS NULL rows, so a
            # second system row sharing a name with a seeded one is allowed.
            session.execute(
                _categories.insert().values(
                    id=uuid.uuid4(),
                    user_id=None,
                    name="Other",
                    color="#111111",
                    icon="other-icon",
                    is_system=True,
                )
            )
            session.commit()
            other = session.execute(
                select(_categories.c.id).where(_categories.c.name == "Other")
            ).all()
            assert len(other) == 2
