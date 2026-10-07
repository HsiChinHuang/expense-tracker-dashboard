"""SQLAlchemy 2.0 engine/session foundation (REQ-TECH-021, REQ-TECH-030).

Provides `create_db_engine` (SQLite PRAGMA wiring per REQ-TECH-032), a
session factory, and the `get_db` request-scoped dependency
(REQ-BE-040, REQ-ARCH-022). PostgreSQL engine selection and the
connect-timeout fallback chain are phase_5_infra scope and deliberately
absent here.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def create_db_engine(database_url: str) -> Engine:
    """Create an Engine for the given URL with SQLite safety wiring.

    For SQLite URLs the engine is built with `check_same_thread=False`
    and executes `PRAGMA foreign_keys=ON` on every new connection so
    foreign keys are enforced per connection (REQ-TECH-032).

    Args:
        database_url: SQLAlchemy database URL (e.g. from DATABASE_URL).

    Returns:
        Engine: The configured, connected-on-demand engine.
    """
    url = make_url(database_url)
    if url.get_backend_name() == "sqlite":
        engine = create_engine(database_url, connect_args={"check_same_thread": False})

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection: Any, _record: Any) -> None:
            """Enable SQLite foreign keys on each new connection."""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine
    return create_engine(database_url)


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
