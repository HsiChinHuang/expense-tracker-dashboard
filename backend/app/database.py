"""SQLAlchemy 2.0 engine/session foundation (REQ-TECH-021, REQ-TECH-030).

Provides `create_db_engine` (SQLite PRAGMA wiring per REQ-TECH-032 plus
the FR-DB-1 PostgreSQL timeout chain and SQLite fallback per
REQ-BE-130/133), a session factory, the `get_db` request-scoped
dependency (REQ-BE-040, REQ-ARCH-022), and the `initialize_database`
startup routine (REQ-BE-131: the fallback path creates tables via
`create_all` and seeds the system categories, never through Alembic —
REQ-DB-083/072).
"""

import logging
from collections.abc import Generator
from typing import Any, Final

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

DB_CONNECT_TIMEOUT: Final[int] = 5
"""PostgreSQL connect timeout in seconds (REQ-BE-130, FR-DB-1)."""

FALLBACK_DATABASE_URL: Final[str] = "sqlite:///./fallback.db"
"""The fixed SQLite fallback target (REQ-BE-133)."""

IS_FALLBACK: bool = False
"""Latched fallback flag: True once the startup probe fell back.

Startup-only by construction (REQ-BE-133): the flag is set exactly once
by `create_db_engine` and never re-evaluated per request; switching
back requires a restart.
"""


def is_fallback() -> bool:
    """Report whether the SQLite fallback is currently active (REQ-BE-132).

    Returns:
        bool: True when the startup probe fell back to SQLite.
    """
    return IS_FALLBACK


def _sqlite_engine(database_url: str) -> Engine:
    """Build a SQLite engine with the PRAGMA wiring (REQ-TECH-032).

    Args:
        database_url: The SQLite SQLAlchemy URL to bind.

    Returns:
        Engine: Engine enforcing `PRAGMA foreign_keys=ON` per connection.
    """
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: Any, _record: Any) -> None:
        """Enable SQLite foreign keys on each new connection."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_db_engine(database_url: str) -> Engine:
    """Create an Engine for the given URL with SQLite safety wiring.

    SQLite URLs build directly with `check_same_thread=False` and
    `PRAGMA foreign_keys=ON` on every new connection (REQ-TECH-032).
    Any other URL attempts PostgreSQL with the named `DB_CONNECT_TIMEOUT`
    connect timeout and, on failure, logs a WARNING and returns a SQLite
    engine on `FALLBACK_DATABASE_URL` with the same PRAGMA wiring,
    latching `IS_FALLBACK` at first probe — startup-only, no per-request
    re-probe (REQ-BE-130/133, FR-DB-1).

    Args:
        database_url: SQLAlchemy database URL (e.g. from DATABASE_URL).

    Returns:
        Engine: The configured, connected-on-demand engine.
    """
    global IS_FALLBACK
    url = make_url(database_url)
    if url.get_backend_name() == "sqlite":
        return _sqlite_engine(database_url)
    if IS_FALLBACK:
        return _sqlite_engine(FALLBACK_DATABASE_URL)
    try:
        engine = create_engine(
            database_url, connect_args={"connect_timeout": DB_CONNECT_TIMEOUT}
        )
        psycopg_connect_probe(database_url)
        return engine
    except (SQLAlchemyError, OSError, ImportError):
        logger.warning(
            "PostgreSQL unreachable for %s; falling back to %s (REQ-BE-130)",
            database_url,
            FALLBACK_DATABASE_URL,
        )
        IS_FALLBACK = True
        return _sqlite_engine(FALLBACK_DATABASE_URL)


PRIMARY_PROBE_PASSED: bool = False
"""Latched once the wire-level connect probe has succeeded (REQ-BE-133):
a successful startup probe is never re-run per request; re-probing
requires a process restart.
"""


def psycopg_connect_probe(database_url: str) -> None:
    """Force the driver import and a real wire connect inside the caller's try.

    `create_engine` resolves the DBAPI driver lazily, so a missing
    psycopg driver or an unreachable primary surfaced only at the first
    `.connect()` — OUTSIDE `create_db_engine`'s `try` — and the REQ-BE-130
    SQLite fallback never engaged (t43 live defect). This probe imports
    psycopg (an `ImportError` propagates straight into the caller's
    except tuple) and performs a real connect attempt; any
    `psycopg.Error` (connection refused, DNS failure, timeout, auth
    failure) is translated to `OSError` so the same except tuple catches
    it and the fallback engages. A passing probe latches
    `PRIMARY_PROBE_PASSED` so later per-request calls skip re-probing
    (startup-only probe, REQ-BE-133).

    Args:
        database_url: The non-SQLite SQLAlchemy URL about to be used.

    Raises:
        ImportError: The psycopg driver is not installed.
        OSError: The psycopg wire layer reported a failure.
    """
    global PRIMARY_PROBE_PASSED
    if PRIMARY_PROBE_PASSED:
        return
    import psycopg

    dsn = make_url(database_url).set(drivername="postgresql").render_as_string(
        hide_password=False
    )
    try:
        connection = psycopg.connect(dsn, connect_timeout=DB_CONNECT_TIMEOUT)
    except psycopg.Error as exc:
        raise OSError("psycopg connect probe failed") from exc
    connection.close()
    PRIMARY_PROBE_PASSED = True


def initialize_database(engine: Engine) -> int:
    """Run the REQ-BE-131 startup initialization for the bound engine.

    When the SQLite fallback is active the tables are created via
    `MetaData.create_all` (NEVER Alembic, REQ-DB-083) and the merged
    system-category seed routine runs afterwards (REQ-DB-072) so the
    ten system categories are always available (REQ-PROD-013). The
    primary path creates no schema and seeds nothing — that stays
    Alembic-owned — and logs primary initialization via `.info(...)`.

    Args:
        engine: Engine built by `create_db_engine` at startup.

    Returns:
        int: Rows inserted by the seed (10 on a fresh fallback database,
        0 on the primary path or an already-seeded fallback file).
    """
    if not is_fallback():
        logger.info(
            "Primary database initialization is Alembic-owned; startup seeds nothing"
        )
        return 0
    from app.models import Base
    from app.scripts.seed import seed_system_categories

    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        return seed_system_categories(connection)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build a session factory bound to the engine.

    Args:
        engine: Engine the sessions will use.

    Returns:
        sessionmaker[Session]: Factory producing new Session objects.
    """
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding one Session per request.

    Yields:
        Session: A database session, closed in a `finally` block even
        when the consumer raises (REQ-BE-040).
    """
    engine = create_db_engine(get_settings().DATABASE_URL)
    factory = create_session_factory(engine)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
