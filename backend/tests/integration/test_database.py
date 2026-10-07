"""Integration tests for the database foundation (t5, REQ-BE-040/TECH-032).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs. The AC
command injects a tmp-file SQLite URL through DATABASE_URL; when the
full suite runs without it, a per-test tmp_path file is used instead so
`backend/dev.db` is never touched.
"""

import os
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import create_db_engine, create_session_factory, get_db


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
    return f"sqlite:///{(tmp_path / 't5_test.db').as_posix()}"


class TestDatabase:
    """Contract coverage for the engine, session factory, and get_db."""

    def test_get_db_yields_and_closes_session(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """get_db yields a Session and closes it on success and on error."""
        monkeypatch.setenv("DATABASE_URL", _sqlite_url(tmp_path))
        get_settings.cache_clear()

        dependency = get_db()
        session = next(dependency)
        assert isinstance(session, Session)

        closed_on_normal_exit = False
        original_close = session.close

        def _track_close() -> None:
            nonlocal closed_on_normal_exit
            closed_on_normal_exit = True
            original_close()

        session.close = _track_close  # type: ignore[method-assign]
        dependency.close()
        assert closed_on_normal_exit is True
        get_settings.cache_clear()

        second = get_db()
        failing = next(second)
        closed_on_exception = False
        original_fail_close = failing.close

        def _track_fail_close() -> None:
            nonlocal closed_on_exception
            closed_on_exception = True
            original_fail_close()

        failing.close = _track_fail_close  # type: ignore[method-assign]
        with pytest.raises(RuntimeError):
            second.throw(RuntimeError("consumer failed"))
        assert closed_on_exception is True
        get_settings.cache_clear()

    def test_sqlite_pragma_foreign_keys_enabled(self, tmp_path: Path) -> None:
        """Sessions from the factory run with PRAGMA foreign_keys = ON."""
        engine = create_db_engine(_sqlite_url(tmp_path))
        factory = create_session_factory(engine)

        with factory() as session:
            enabled = session.connection().exec_driver_sql(
                "PRAGMA foreign_keys"
            ).scalar_one()

        engine.dispose()

        assert int(enabled) == 1
