"""Unit tests for the t79 business counters and the fallback gauge.

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs. The node
names deliberately do not spell a metric name -- the names live once,
in ``backend/app/telemetry.py``, behind the constants the services
import.

Method: every counter assertion is a DELTA read from
``app.telemetry.exposition_body()`` (the exact bytes the loopback-gated
``/metrics`` route serves), never an in-process spy. ``create_app()``
runs first so the idempotent ``setup_telemetry`` has installed the
provider and registered the business instruments; the database is a
private SQLite file per test under ``tmp_path`` with the schema via
``Base.metadata.create_all`` (the merged t11/t13 unit isolation
pattern). The fallback node mutates the latch OWNER's module
attribute directly -- the gauge callback reads it at scrape time, so
the node proves the series is live in both latch states.
"""

import re
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import AppError
from app.database import IS_FALLBACK, create_db_engine
from app.main import create_app
from app.models import Base
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User
from app.services import category_service, expense_service
from app.telemetry import (
    CATEGORY_CREATED_TOTAL,
    DB_FALLBACK_ACTIVE,
    EXPENSE_CREATE_FAILURES_TOTAL,
    EXPENSE_CREATED_TOTAL,
    exposition_body,
)

SAMPLE_PATTERN = "^{name}(?:\\{{[^}}]*\\}})? ([0-9.eE+-]+)$"


def _sample(name: str) -> float:
    """Return the current exposition value of one unprefixed series.

    Args:
        name: The metric name as the alerts.yaml inventory declares it.

    Returns:
        float: The sample value, or 0.0 while the series is absent.
    """
    body = exposition_body().decode()
    match = re.search(SAMPLE_PATTERN.format(name=name), body, re.MULTILINE)
    return 0.0 if match is None else float(match.group(1))


def _factory(tmp_path: Path, name: str) -> tuple[sessionmaker[Session], User, Category]:
    """Build this test's SQLite file, schema, user and category.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        tuple: Session factory plus refreshed user and category handles.
    """
    create_app()
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        user = User(email="t79@example.com", username="t79", hashed_password="x")
        session.add(user)
        session.commit()
        category = Category(name="T79", color="#010203", user_id=user.id)
        session.add(category)
        session.commit()
        session.refresh(user)
        session.refresh(category)
    return factory, user, category


class TestBusinessCounters:
    """Contract coverage for the three create-path counters."""

    def test_create_expense_advances_the_success_counter_by_one(
        self, tmp_path: Path
    ) -> None:
        """One persisted expense moves its counter by 1 and only its own."""
        factory, user, category = _factory(tmp_path, "expense_ok")
        before = {
            EXPENSE_CREATED_TOTAL: _sample(EXPENSE_CREATED_TOTAL),
            EXPENSE_CREATE_FAILURES_TOTAL: _sample(EXPENSE_CREATE_FAILURES_TOTAL),
            CATEGORY_CREATED_TOTAL: _sample(CATEGORY_CREATED_TOTAL),
        }

        with factory() as session:
            expense_service.create_expense(
                session,
                user,
                amount="12.34",
                category_id=category.id,
                date=date(2026, 10, 16),
                note=None,
            )

        assert _sample(EXPENSE_CREATED_TOTAL) - before[EXPENSE_CREATED_TOTAL] == 1
        assert _sample(EXPENSE_CREATE_FAILURES_TOTAL) == before[EXPENSE_CREATE_FAILURES_TOTAL]
        assert _sample(CATEGORY_CREATED_TOTAL) == before[CATEGORY_CREATED_TOTAL]

    def test_create_category_advances_the_category_counter_by_one(
        self, tmp_path: Path
    ) -> None:
        """One persisted category moves its counter by 1 and only its own."""
        factory, user, _ = _factory(tmp_path, "category_ok")
        before = {
            EXPENSE_CREATED_TOTAL: _sample(EXPENSE_CREATED_TOTAL),
            EXPENSE_CREATE_FAILURES_TOTAL: _sample(EXPENSE_CREATE_FAILURES_TOTAL),
            CATEGORY_CREATED_TOTAL: _sample(CATEGORY_CREATED_TOTAL),
        }

        with factory() as session:
            category_service.create_category(session, user, "T79Second", "#040506", None)

        assert _sample(CATEGORY_CREATED_TOTAL) - before[CATEGORY_CREATED_TOTAL] == 1
        assert _sample(EXPENSE_CREATED_TOTAL) == before[EXPENSE_CREATED_TOTAL]
        assert _sample(EXPENSE_CREATE_FAILURES_TOTAL) == before[EXPENSE_CREATE_FAILURES_TOTAL]

    def test_failed_expense_create_advances_the_failure_counter_and_reraises(
        self, tmp_path: Path
    ) -> None:
        """The 422 leg counts once and the AppError keeps its identity."""
        factory, user, category = _factory(tmp_path, "expense_fail")
        before = {
            EXPENSE_CREATED_TOTAL: _sample(EXPENSE_CREATED_TOTAL),
            EXPENSE_CREATE_FAILURES_TOTAL: _sample(EXPENSE_CREATE_FAILURES_TOTAL),
            CATEGORY_CREATED_TOTAL: _sample(CATEGORY_CREATED_TOTAL),
        }

        try:
            with factory() as session:
                expense_service.create_expense(
                    session,
                    user,
                    amount="abc",
                    category_id=category.id,
                    date=date(2026, 10, 16),
                    note=None,
                )
            raise AssertionError("the invalid amount must still raise AppError")
        except AppError as error:
            assert error.status_code == 422
            assert error.code == "INVALID_AMOUNT"
            assert error.field == "amount"

        assert _sample(EXPENSE_CREATE_FAILURES_TOTAL) - before[EXPENSE_CREATE_FAILURES_TOTAL] == 1
        assert _sample(EXPENSE_CREATED_TOTAL) == before[EXPENSE_CREATED_TOTAL]
        assert _sample(CATEGORY_CREATED_TOTAL) == before[CATEGORY_CREATED_TOTAL]
        with factory() as session:
            assert len(session.scalars(select(Expense)).all()) == 0


class TestFallbackGauge:
    """Contract coverage for the db_fallback_active callback gauge."""

    def test_fallback_gauge_reads_the_latched_flag(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The gauge answers 0 with the latch False and 1 with it True."""
        import app.database as database_module

        assert IS_FALLBACK is False, "the unit suite must run on the non-fallback latch"
        create_app()
        assert _sample(DB_FALLBACK_ACTIVE) == 0.0
        monkeypatch.setattr(database_module, "IS_FALLBACK", True)
        try:
            assert _sample(DB_FALLBACK_ACTIVE) == 1.0
        finally:
            monkeypatch.undo()
        assert _sample(DB_FALLBACK_ACTIVE) == 0.0
