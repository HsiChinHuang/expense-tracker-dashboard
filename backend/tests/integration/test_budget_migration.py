"""Integration tests for Alembic revision 005 (t14 ac1, ac6).

Class and function names are part of the issue contract. The schema is
applied through Alembic's Python API (``command.upgrade``/
``command.downgrade`` with an absolute ``script_location``) — never
``Base.metadata.create_all`` — so the DDL under test is the migration's
own (COPY of the tests/integration/test_expense_migration.py harness;
there is no conftest.py). ``DATABASE_URL`` is pointed at a per-test file
via ``monkeypatch`` + ``get_settings.cache_clear()``.
"""

from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text

from alembic import command
from app.config import get_settings
from app.database import create_db_engine

BACKEND_DIR = Path(__file__).resolve().parents[2]

BUDGET_CONSTRAINTS = {
    "uq_budgets_user_month",
    "ck_budgets_amount_positive",
    "ck_budgets_year_month_format",
}


def _config() -> Config:
    """Build an Alembic Config pointing at this backend's alembic dir.

    Returns:
        Config: Config with an absolute ``script_location``.
    """
    config = Config()
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


def _migrate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    revision: str = "head",
) -> Engine:
    """Run `alembic upgrade <revision>` onto a per-test SQLite file.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        monkeypatch: pytest fixture used to point DATABASE_URL (which
            the online ``env.py`` reads through ``get_settings``) at
            this test's file for the duration of the migration.
        name: Test-specific file name so no two tests share a file.
        revision: Alembic revision to upgrade to (default: head).

    Returns:
        Engine: An engine over the freshly migrated database with
            SQLite foreign keys enabled.
    """
    url = f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    try:
        command.upgrade(_config(), revision)
    finally:
        get_settings.cache_clear()
    return create_db_engine(url)


def _tables(engine: Engine) -> set[str]:
    """Return the SQLite table names present in ``engine``'s database.

    Args:
        engine: Engine over a migrated (or downgraded) database.

    Returns:
        set[str]: Table names from ``sqlite_master``.
    """
    with engine.connect() as connection:
        return set(
            connection.execute(
                text("select name from sqlite_master where type = 'table'")
            )
            .scalars()
            .all()
        )


def _budget_ddl(engine: Engine) -> str:
    """Return the CREATE TABLE DDL Alembic wrote for ``budgets``.

    Args:
        engine: Engine over a database where the table exists.

    Returns:
        str: The stored DDL text (named CHECKs appear inline).
    """
    with engine.connect() as connection:
        ddl = connection.execute(
            text("select sql from sqlite_master where type = 'table' and name = 'budgets'")
        ).scalar_one()
    return str(ddl)


SEED_SQL = [
    "insert into users (id, email, username, hashed_password, is_active, created_at, updated_at)"
    " values ('11111111-1111-1111-1111-111111111111', 'a@b.com', 'alice', 'x', 1,"
    " '2026-01-01 00:00:00', '2026-01-01 00:00:00')",
    "insert into budgets (id, user_id, year_month, amount, created_at, updated_at)"
    " values ('44444444-4444-4444-4444-444444444444',"
    " '11111111-1111-1111-1111-111111111111', '2026-10', 2000.00,"
    " '2026-10-01 00:00:00', '2026-10-01 00:00:00')",
]


class TestBudgetMigration:
    """Contract coverage for revision 005 (t14 ac1, ac6)."""

    def test_upgrade_head_creates_budgets_with_three_named_constraints(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """upgrade head lands on 005 with the table + three named constraints."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_upgrade_head_creates_budgets_with_three_named_constraints",
        )
        assert "budgets" in _tables(engine)
        with engine.connect() as connection:
            version = connection.execute(
                text("select version_num from alembic_version")
            ).scalar_one()
            assert version == "005"

        ddl = _budget_ddl(engine)
        compact = ddl.replace(" ", "")
        for name in BUDGET_CONSTRAINTS:
            assert name in ddl, ddl
        assert "amount>0" in compact, ddl
        assert "year_monthGLOB'[0-9][0-9][0-9][0-9]-[0-9][0-9]'" in compact, ddl
        assert "unique(user_id,year_month)" in compact.lower(), ddl
        assert "ON DELETE CASCADE" in ddl.upper(), ddl
        engine.dispose()

    def test_downgrade_005_to_004_drops_budgets_and_upgrade_roundtrip_restores(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """005 -> 004 removes the table; re-upgrade restores it (round-trip)."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_downgrade_005_to_004_drops_budgets_and_upgrade_roundtrip_restores",
        )
        assert "budgets" in _tables(engine)

        url = engine.url
        monkeypatch.setenv("DATABASE_URL", str(url))
        get_settings.cache_clear()
        try:
            command.downgrade(_config(), "004")
        finally:
            get_settings.cache_clear()

        assert "budgets" not in _tables(engine)
        with engine.connect() as connection:
            version = connection.execute(
                text("select version_num from alembic_version")
            ).scalar_one()
            assert version == "004"

        monkeypatch.setenv("DATABASE_URL", str(url))
        get_settings.cache_clear()
        try:
            command.upgrade(_config(), "head")
        finally:
            get_settings.cache_clear()

        assert "budgets" in _tables(engine)
        ddl = _budget_ddl(engine)
        for name in BUDGET_CONSTRAINTS:
            assert name in ddl, ddl
        engine.dispose()

    def test_raw_delete_of_owner_cascades_to_budget_rows(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Raw DELETE of the owner removes their budgets (FK CASCADE, REQ-DB-042)."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_raw_delete_of_owner_cascades_to_budget_rows",
        )
        with engine.begin() as connection:
            for statement in SEED_SQL:
                connection.execute(text(statement))

        with engine.begin() as connection:
            connection.execute(
                text("delete from users where id = '11111111-1111-1111-1111-111111111111'")
            )

        with engine.connect() as connection:
            surviving = connection.execute(
                text("select count(*) from budgets")
            ).scalar_one()
            assert surviving == 0
        engine.dispose()

    def test_alembic_heads_is_single_revision_005(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The chain stays linear with exactly one head: 005 (ac6 pin)."""
        # heads/capabilities need no live database; DATABASE_URL is still
        # pointed at a per-test file so nothing can touch backend/dev.db.
        url = (
            "sqlite:///"
            + (tmp_path / "test_alembic_heads_is_single_revision_005.db").as_posix()
        )
        monkeypatch.setenv("DATABASE_URL", url)
        get_settings.cache_clear()
        try:
            heads = ScriptDirectory.from_config(_config()).get_heads()
        finally:
            get_settings.cache_clear()
        assert heads == ["005"], heads
