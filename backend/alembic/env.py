"""Alembic environment for the expense-tracker backend (t5).

Online mode builds the engine from the app Settings (which honor
DATABASE_URL via env var > .env > default, REQ-ARCH-061) and configures
a live connection before running migrations, so `alembic upgrade head`
actually connects even with a zero-revision chain. No URL is hardcoded.
"""

from sqlalchemy.engine import Engine

from alembic import context
from app.config import get_settings
from app.database import create_db_engine
from app.models.user import Base

config = context.config

target_metadata = Base.metadata
"""Model metadata for autogenerate; t6 registers only the users table."""


def run_migrations_online() -> None:
    """Run migrations against the database from app settings.

    The engine is created before `context.configure` so a real
    connection is opened even when the revision chain is empty.
    """
    engine: Engine = create_db_engine(get_settings().DATABASE_URL)

    with engine.begin() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

    engine.dispose()


run_migrations_online()
