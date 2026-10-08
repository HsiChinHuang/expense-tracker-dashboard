"""Integration tests for Alembic revision 002 (t10 ac2/ac4).

Class and function names are part of the issue contract. The schema is
applied through Alembic's Python API (``command.upgrade`` with an
absolute ``script_location``) — never ``Base.metadata.create_all`` — so
the DDL under test is the migration's own (isolation contract,
docs/issues/t10.md). ``DATABASE_URL`` is pointed at a per-test file via
``monkeypatch`` + ``get_settings.cache_clear()`` and pytest undoes the
environment change afterwards.
"""

from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from app.config import get_settings
from app.database import create_db_engine, create_session_factory
from app.models import Category, User
from app.scripts.seed import SYSTEM_CATEGORIES

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _migrate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    revision: str = "head",
) -> Engine:
    """Run `alembic upgrade head` onto a per-test SQLite file.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        monkeypatch: pytest fixture used to point DATABASE_URL (which
            the online ``env.py`` reads through ``get_settings``) at
            this test's file for the duration of the migration.
        name: Test-specific file name so no two tests share a file.

    Returns:
        Engine: An engine over the freshly migrated (revision 002)
            database with SQLite foreign keys enabled.
    """
    url = f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    try:
        config = Config()
        config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
        command.upgrade(config, revision)
    finally:
        get_settings.cache_clear()
    return create_db_engine(url)


def _session(engine: Engine) -> Session:
    """Return a Session bound to ``engine``.

    Args:
        engine: Engine over a migrated database.

    Returns:
        Session: A fresh session.
    """
    factory: sessionmaker[Session] = create_session_factory(engine)
    return factory()


class TestCategoryMigration:
    """Contract coverage for revision 002 (t10 ac2, ac4)."""

    def test_duplicate_custom_name_raises_and_two_system_rows_are_allowed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The partial unique index is scoped to user-owned rows only."""
        engine = _migrate(
            tmp_path, monkeypatch, "test_duplicate_custom_name_raises"
        )
        with _session(engine) as session:
            owner = User(
                email="dup-cat@example.com",
                username="dupcat",
                hashed_password="x" * 60,
            )
            session.add(owner)
            session.commit()
            owner_id = owner.id

        with _session(engine) as session:
            session.add(
                Category(name="Lunch", color="#EF4444", user_id=owner_id)
            )
            session.commit()

        with _session(engine) as session, pytest.raises(IntegrityError):
            session.add(
                Category(name="Lunch", color="#22C55E", user_id=owner_id)
            )
            session.commit()

        with _session(engine) as session:
            # Two user_id IS NULL rows sharing a name are both accepted:
            # the partial predicate excludes system rows (REQ-DB-022).
            session.add_all(
                [
                    Category(name="Extra System", color="#111111", is_system=True),
                    Category(name="Extra System", color="#222222", is_system=True),
                ]
            )
            session.commit()
            count = (
                session.query(Category)
                .filter(Category.name == "Extra System")
                .count()
            )
            assert count == 2
        engine.dispose()

    def test_revision_002_registers_only_the_categories_table(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """After upgrade head the table set is users+categories+alembic."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_revision_002_registers_only_the_categories_table",
            # t12 amendment (t10 precedent): head is 003 now, so pin this
            # revision-002-shape assertion to 002 explicitly.
            revision="002",
        )
        with engine.connect() as connection:
            tables = set(
                connection.execute(
                    text(
                        "select name from sqlite_master where type = 'table'"
                    )
                )
                .scalars()
                .all()
            )
            assert tables == {"users", "categories", "alembic_version"}, tables
            version = connection.execute(
                text("select version_num from alembic_version")
            ).scalar_one()
            assert version == "002"
        engine.dispose()

    def test_upgrade_head_seeds_exactly_ten_system_categories(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`upgrade head` alone leaves exactly the ten seeded system rows."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_upgrade_head_seeds_exactly_ten_system_categories",
        )
        with _session(engine) as session:
            rows = (
                session.query(Category.name, Category.color, Category.icon)
                .all()
            )
            assert len(rows) == 10
            expected = [
                (r["name"], r["color"], r["icon"]) for r in SYSTEM_CATEGORIES
            ]
            assert sorted(rows) == sorted(expected)

        with engine.connect() as connection:
            shape = connection.execute(
                text(
                    "select count(*) from categories "
                    "where is_system = 1 and user_id is null"
                )
            ).scalar_one()
            assert shape == 10
            distinct = connection.execute(
                text("select count(distinct id) from categories")
            ).scalar_one()
            assert distinct == 10
        engine.dispose()
