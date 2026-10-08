"""Integration tests for Alembic revision 003 (t12 ac1/ac5).

Class and function names are part of the issue contract. The schema is
applied through Alembic's Python API (``command.upgrade``/
``command.downgrade`` with an absolute ``script_location``) — never
``Base.metadata.create_all`` — so the DDL under test is the migration's
own (COPY of the tests/integration/test_category_migration.py harness;
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


def _audit_ddl(engine: Engine) -> str:
    """Return the CREATE TABLE DDL Alembic wrote for ``audit_logs``.

    Args:
        engine: Engine over a database where the table exists.

    Returns:
        str: The stored DDL text (named CHECKs appear inline).
    """
    with engine.connect() as connection:
        ddl = connection.execute(
            text(
                "select sql from sqlite_master "
                "where type = 'table' and name = 'audit_logs'"
            )
        ).scalar_one()
    return str(ddl)


class TestAuditMigration:
    """Contract coverage for revision 003 (t12 ac1, ac5)."""

    def test_upgrade_head_creates_audit_logs_with_named_checks_and_three_indexes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """upgrade head lands on 003 with table + named CHECKs + indexes."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_upgrade_head_creates_audit_logs_with_named_checks",
        )
        assert "audit_logs" in _tables(engine)
        with engine.connect() as connection:
            version = connection.execute(
                text("select version_num from alembic_version")
            ).scalar_one()
            assert version == "003"

        ddl = _audit_ddl(engine)
        assert "ck_audit_action" in ddl, ddl
        assert "ck_audit_entity_type" in ddl, ddl
        assert "'CREATE','UPDATE','DELETE'" in ddl.replace(" ", ""), ddl
        assert "'expense','budget'" in ddl.replace(" ", ""), ddl

        assert {
            "idx_audit_user_created",
            "idx_audit_entity",
            "idx_audit_action",
        } <= _index_names(engine)
        engine.dispose()

    def test_downgrade_003_to_002_drops_audit_logs_and_upgrade_roundtrip_restores(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """003 -> 002 removes table + index names; re-upgrade restores all."""
        engine = _migrate(
            tmp_path,
            monkeypatch,
            "test_downgrade_003_to_002_drops_audit_logs_and_roundtrip",
        )
        assert "audit_logs" in _tables(engine)

        url = engine.url
        monkeypatch.setenv("DATABASE_URL", str(url))
        get_settings.cache_clear()
        try:
            command.downgrade(_config(), "002")
        finally:
            get_settings.cache_clear()

        assert "audit_logs" not in _tables(engine)
        audit_indexes = {
            "idx_audit_user_created",
            "idx_audit_entity",
            "idx_audit_action",
        }
        assert not audit_indexes & _index_names(engine)
        with engine.connect() as connection:
            version = connection.execute(
                text("select version_num from alembic_version")
            ).scalar_one()
            assert version == "002"

        monkeypatch.setenv("DATABASE_URL", str(url))
        get_settings.cache_clear()
        try:
            command.upgrade(_config(), "head")
        finally:
            get_settings.cache_clear()

        assert "audit_logs" in _tables(engine)
        assert audit_indexes <= _index_names(engine)
        ddl = _audit_ddl(engine)
        assert "ck_audit_action" in ddl and "ck_audit_entity_type" in ddl, ddl
        engine.dispose()

    def test_alembic_heads_is_single_revision_003(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The chain stays linear with exactly one head: 003 (ac5 pin)."""
        # heads/capabilities need no live database; DATABASE_URL is still
        # pointed at a per-test file so nothing can touch backend/dev.db.
        url = f"sqlite:///{(tmp_path / 'test_alembic_heads_is_single_revision_003.db').as_posix()}"
        monkeypatch.setenv("DATABASE_URL", url)
        get_settings.cache_clear()
        try:
            heads = ScriptDirectory.from_config(_config()).get_heads()
        finally:
            get_settings.cache_clear()
        assert heads == ["003"], heads
