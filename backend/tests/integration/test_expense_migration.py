"""Integration tests for Alembic revision 004 (t13 ac1, ac6).

Class and function names are part of the issue contract. The schema is
applied through Alembic's Python API (``command.upgrade``/
``command.downgrade`` with an absolute ``script_location``) — never
``Base.metadata.create_all`` — so the DDL under test is the migration's
own (COPY of the tests/integration/test_audit_migration.py harness;
there is no conftest.py). ``DATABASE_URL`` is pointed at a per-test file
via ``monkeypatch`` + ``get_settings.cache_clear()``.
"""

from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError

from alembic import command
from app.config import get_settings
from app.database import create_db_engine

BACKEND_DIR = Path(__file__).resolve().parents[2]

EXPENSE_INDEXES = {
    "idx_expenses_user_id",
    "idx_expenses_user_date",
    "idx_expenses_user_category",
    "idx_expenses_category_id",
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


def _run(
    monkeypatch: pytest.MonkeyPatch, engine: Engine, statement: str
) -> None:
    """Execute one raw statement against ``engine``.

    Args:
        monkeypatch: Unused fixture kept for call-site symmetry.
        engine: Target engine.
        statement: The SQL to run.

    Returns:
        None
    """
    with engine.begin() as connection:
        connection.execute(text(statement))


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


def _index_names(engine: Engine) -> set[str]:
    """Return the SQLite index names present in ``engine``'s database.

    Args:
        engine: Engine over a migrated (or downgraded) database.

    Returns:
        set[str]: Index names from ``sqlite_master``.
    """
    with engine.connect() as connection:
        return set(
            connection.execute(
                text("select name from sqlite_master where type = 'index'")
            )
            .scalars()
            .all()
        )


def _expense_ddl(engine: Engine) -> str:
    """Return the CREATE TABLE DDL Alembic wrote for ``expenses``.

    Args:
        engine: Engine over a database where the table exists.

    Returns:
        str: The stored DDL text (named CHECKs appear inline).
    """
    with engine.connect() as connection:
        ddl = connection.execute(
            text("select sql from sqlite_master where type = 'table' and name = 'expenses'")
        ).scalar_one()
    return str(ddl)


SEED_SQL = [
    "insert into users (id, email, username, hashed_password, is_active, created_at, updated_at)"
    " values ('11111111-1111-1111-1111-111111111111', 'a@b.com', 'alice', 'x', 1,"
    " '2026-01-01 00:00:00', '2026-01-01 00:00:00')",
    "insert into categories (id, user_id, name, color, is_system, created_at)"
    " values ('22222222-2222-2222-2222-222222222222',"
    " '11111111-1111-1111-1111-111111111111', 'Groceries', '#112233', 0,"
    " '2026-01-01 00:00:00')",
    "insert into expenses (id, user_id, category_id, amount, currency, date, note,"
    " created_at, updated_at) values ('33333333-3333-3333-3333-333333333333',"
    " '11111111-1111-1111-1111-111111111111',"
    " '22222222-2222-2222-2222-222222222222', 10.00, 'USD', '2026-01-15', 'n',"
    " '2026-01-15 00:00:00', '2026-01-15 00:00:00')",
]


class TestExpenseMigration:
    """Contract coverage for revision 004 (t13 ac1, ac6)."""

    def test_upgrade_head_creates_expenses_with_named_checks_and_four_indexes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """upgrade head lands on 004 with table + named CHECKs + indexes."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_upgrade_head_creates_expenses_with_named_checks",
        )
        assert "expenses" in _tables(engine)
        with engine.connect() as connection:
            version = connection.execute(
                text("select version_num from alembic_version")
            ).scalar_one()
            assert version == "004"

        ddl = _expense_ddl(engine)
        assert "ck_expenses_amount_positive" in ddl, ddl
        assert "ck_expenses_currency_usd" in ddl, ddl
        assert "amount>0" in ddl.replace(" ", ""), ddl
        assert "currency='USD'" in ddl.replace(" ", ""), ddl
        assert "ON DELETE CASCADE" in ddl.upper(), ddl
        assert "ON DELETE RESTRICT" in ddl.upper(), ddl

        assert EXPENSE_INDEXES <= _index_names(engine)
        engine.dispose()

    def test_downgrade_004_to_003_drops_expenses_and_upgrade_roundtrip_restores(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """004 -> 003 removes table + index names; re-upgrade restores all."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_downgrade_004_to_003_drops_expenses_and_roundtrip",
        )
        assert "expenses" in _tables(engine)

        url = engine.url
        monkeypatch.setenv("DATABASE_URL", str(url))
        get_settings.cache_clear()
        try:
            command.downgrade(_config(), "003")
        finally:
            get_settings.cache_clear()

        assert "expenses" not in _tables(engine)
        assert not EXPENSE_INDEXES & _index_names(engine)
        with engine.connect() as connection:
            version = connection.execute(
                text("select version_num from alembic_version")
            ).scalar_one()
            assert version == "003"

        monkeypatch.setenv("DATABASE_URL", str(url))
        get_settings.cache_clear()
        try:
            command.upgrade(_config(), "head")
        finally:
            get_settings.cache_clear()

        assert "expenses" in _tables(engine)
        assert EXPENSE_INDEXES <= _index_names(engine)
        ddl = _expense_ddl(engine)
        assert "ck_expenses_amount_positive" in ddl and "ck_expenses_currency_usd" in ddl, ddl
        engine.dispose()

    def test_raw_delete_of_used_category_violates_the_restrict_fk(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Raw DELETE of a referenced category raises, row survives (REQ-DB-032)."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_raw_delete_of_used_category_violates_the_restrict_fk",
        )
        for statement in SEED_SQL:
            _run(monkeypatch, engine, statement)

        with pytest.raises(IntegrityError):
            _run(
                monkeypatch,
                engine,
                "delete from categories where id ="
                " '22222222-2222-2222-2222-222222222222'",
            )

        with engine.connect() as connection:
            surviving = connection.execute(
                text(
                    "select count(*) from categories where id ="
                    " '22222222-2222-2222-2222-222222222222'"
                )
            ).scalar_one()
            assert surviving == 1
        engine.dispose()

    def test_alembic_heads_is_single_revision_004(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The chain stays linear with exactly one head: 004 (ac6 pin)."""
        # heads/capabilities need no live database; DATABASE_URL is still
        # pointed at a per-test file so nothing can touch backend/dev.db.
        url = (
            "sqlite:///"
            + (tmp_path / "test_alembic_heads_is_single_revision_004.db").as_posix()
        )
        monkeypatch.setenv("DATABASE_URL", url)
        get_settings.cache_clear()
        try:
            heads = ScriptDirectory.from_config(_config()).get_heads()
        finally:
            get_settings.cache_clear()
        assert heads == ["004"], heads
