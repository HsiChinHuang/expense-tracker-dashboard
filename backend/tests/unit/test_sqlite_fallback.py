"""Unit tests for the SQLite fallback engine chain (t25 ac1/ac2/ac5).

Node IDs are part of the issue contract: the AC verification commands
reference these exact pytest node IDs. The suite is hermetic — no live
PostgreSQL server exists here (the ``psycopg`` driver is not even
installed), so the unreachable-primary legs use the refused loopback URL
``postgresql+psycopg://t25:t25@127.0.0.1:1/t25_probe`` (closed port, no
egress) and the timeout hand-off leg monkeypatches ``create_engine``
through ``app.database`` and records its ``connect_args`` (W7b).

Every node APPENDS its own ``rc=0`` evidence lines to
``tests/sqlite_fallback_evidence.txt`` (gitignored, absolute-path writes
via ``Path(__file__)``) and writes ONLY on success, so every ``grep -q``
in the pinned AC commands is fail-before-capable and any subset of nodes
can run in any order.
"""

import builtins
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy import MetaData, create_engine, inspect, make_url
from sqlalchemy.engine import Engine as SaEngine

from app import database
from app.config import get_settings

REFUSED_URL = "postgresql+psycopg://t25:t25@127.0.0.1:1/t25_probe"
EVIDENCE = (Path(__file__).parent.parent / "sqlite_fallback_evidence.txt").as_posix()


def _record(line: str) -> None:
    """Append one evidence line to the shared evidence file.

    Args:
        line: The full line (ending ``rc=0``) to append.
    """
    with Path(EVIDENCE).open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _fake_primary(
    monkeypatch: MonkeyPatch,
    on_primary: Callable[[str, dict[str, Any]], SaEngine],
) -> None:
    """Route non-SQLite create_engine calls through ``on_primary``.

    Args:
        monkeypatch: pytest monkeypatch for the attribute swap.
        on_primary: Callable ``(url, kwargs)`` invoked for every
            non-SQLite create_engine call; may raise to simulate the
            driver-absent / refused primary.
    """
    real = create_engine

    def _fake(url: str, **kwargs: Any) -> SaEngine:
        if make_url(url).get_backend_name() != "sqlite":
            return on_primary(url, kwargs)
        return real(url, **kwargs)

    monkeypatch.setattr(database, "create_engine", _fake)


@pytest.fixture(autouse=True)
def _reset_fallback_state(monkeypatch: MonkeyPatch) -> Any:
    """Reset the latched flag and settings cache before and after.

    Without this the latched ``IS_FALLBACK`` leaks across nodes in the
    single pytest process (issue state-hygiene pin).

    Args:
        monkeypatch: pytest monkeypatch for the flag reset.

    Yields:
        Any: Control returns to the test with a clean fallback state.
    """
    monkeypatch.setattr(database, "IS_FALLBACK", False)
    get_settings.cache_clear()
    yield
    monkeypatch.setattr(database, "IS_FALLBACK", False)
    get_settings.cache_clear()


def test_sqlite_url_keeps_pragma_and_reports_no_fallback(tmp_path: Path) -> None:
    """A SQLite URL builds directly: PRAGMA on, fallback never touched."""
    engine = database.create_db_engine(f"sqlite:///{(tmp_path / 'u1.db').as_posix()}")

    enabled = engine.connect().exec_driver_sql("PRAGMA foreign_keys").scalar_one()

    assert int(enabled) == 1
    assert database.is_fallback() is False
    _record("UNIT_SQLITE_PRAGMA ok rc=0")
    engine.dispose()


def test_refused_postgres_url_falls_back_under_five_seconds(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Refused primary: fallback engine within the 5-second budget."""
    monkeypatch.chdir(tmp_path)

    started = time.perf_counter()
    engine = database.create_db_engine(REFUSED_URL)
    elapsed = time.perf_counter() - started

    assert engine.url.get_backend_name() == "sqlite"
    assert str(engine.url) == database.FALLBACK_DATABASE_URL
    assert database.is_fallback() is True
    assert elapsed < 5.0
    _record(f"FALLBACK_TIMING_REFUSED elapsed={elapsed:.3f} fallback=true rc=0")
    engine.dispose()


def test_startup_passes_connect_timeout_from_the_named_constant(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """The PostgreSQL attempt hands connect_timeout=DB_CONNECT_TIMEOUT."""
    monkeypatch.chdir(tmp_path)
    captured: dict[str, Any] = {}

    def _raise_driver_absent(url: str, kwargs: dict[str, Any]) -> SaEngine:
        captured["url"] = url
        captured["connect_args"] = kwargs.get("connect_args")
        msg = "psycopg not installed (measured hermetic state)"
        raise ModuleNotFoundError(msg)

    _fake_primary(monkeypatch, _raise_driver_absent)

    engine = database.create_db_engine(REFUSED_URL)

    assert captured["url"] == REFUSED_URL
    assert captured["connect_args"] is not None
    assert captured["connect_args"]["connect_timeout"] == database.DB_CONNECT_TIMEOUT
    assert database.DB_CONNECT_TIMEOUT == 5
    assert database.is_fallback() is True
    assert engine.url.get_backend_name() == "sqlite"
    _record(
        "FALLBACK_CAPS connect_timeout=5 attempted=postgresql+psycopg "
        "fallback=true rc=0"
    )
    engine.dispose()


def test_startup_probes_the_primary_once_and_then_stops(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """REQ-BE-133 startup-only: after latching, later calls never re-probe."""
    monkeypatch.chdir(tmp_path)
    probes: list[str] = []

    def _refuse(url: str, kwargs: dict[str, Any]) -> SaEngine:
        probes.append(url)
        msg = "connection refused"
        raise OSError(msg)

    _fake_primary(monkeypatch, _refuse)

    first = database.create_db_engine(REFUSED_URL)
    second = database.create_db_engine(REFUSED_URL)

    assert database.is_fallback() is True
    assert probes == [REFUSED_URL]
    assert first.url.get_backend_name() == "sqlite"
    assert second.url.get_backend_name() == "sqlite"
    _record(f"FALLBACK_SINGLE_PROBE probes={len(probes)} fallback=true rc=0")


def test_startup_initializes_the_fallback_target_once(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Fallback init: create_all exactly once, 10 rows, five fixed tables,
    and provably NO alembic import anywhere on the path (REQ-DB-083)."""
    monkeypatch.chdir(tmp_path)
    database.IS_FALLBACK = True
    engine = database._sqlite_engine(f"sqlite:///{(tmp_path / 'fallback.db').as_posix()}")

    create_all_calls: list[int] = []
    real_create_all = MetaData.create_all

    def _counting_create_all(self: MetaData, *args: Any, **kwargs: Any) -> None:
        create_all_calls.append(1)
        real_create_all(self, *args, **kwargs)

    monkeypatch.setattr(MetaData, "create_all", _counting_create_all)

    alembic_imports: list[str] = []
    real_import = builtins.__import__

    def _watch_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.split(".")[0] == "alembic":
            alembic_imports.append(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _watch_import)

    seeded = database.initialize_database(engine)

    def _sorted_names() -> list[str]:
        insp = inspect(engine)
        present = {t for t, _ in insp.get_sorted_table_and_fkc_names() if t is not None}
        deps = {
            name: {fk["referred_table"] for fk in insp.get_foreign_keys(name)}
            for name in present
        }
        contract = ["users", "categories", "expenses", "budgets", "audit_logs"]
        assert present == set(contract)
        ordered: list[str] = []
        remaining = set(present)
        while remaining:
            for name in contract:
                if name in remaining and deps[name].isdisjoint(remaining):
                    ordered.append(name)
                    remaining.discard(name)
                    break
        return ordered

    tables = _sorted_names()

    assert seeded == 10
    assert len(create_all_calls) == 1
    assert tables == ["users", "categories", "expenses", "budgets", "audit_logs"]
    assert alembic_imports == []
    _record("FALLBACK_SEED_COUNT 10 rc=0")
    _record("FALLBACK_CREATE_ALL_CALLS 1 rc=0")
    _record("FALLBACK_TABLES users,categories,expenses,budgets,audit_logs rc=0")
    _record("FALLBACK_NO_ALEMBIC_IMPORT alembic=absent rc=0")
    engine.dispose()
