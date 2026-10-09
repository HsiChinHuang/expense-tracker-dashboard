"""Unit tests for app.services.dashboard_service (t19 ac2..ac5).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs (46-node
frozen inventory, docs/issues/t19.md).

Isolation follows the merged t11/t13/t14 unit pattern (no
conftest.py): one private SQLite file PER TEST under ``tmp_path``,
schema via ``Base.metadata.create_all``, assertions run against
PERSISTED content read back through a FRESH session. The service is
read-only, so no audit/rollback seam is exercised here.

Contract pins exercised here (issue ac2/ac3/ac4/ac5):

* Money fields are 2-dp STRINGS end to end; ``percentage`` is the one
  JSON number (None exactly when the budget is 0); ``is_over_budget``
  is ``total > budget AND budget > 0``; ``remaining`` may be negative.
* ``get_trend`` / ``get_heatmap`` receive the pinned ``today=``
  determinism kwarg (groom ruling 6) so no test reads the wall clock.
* The frozen key sets: summary 7 keys, by-category rows 5 keys, trend
  items ``{year_month, total}``, cumulative day keys ``{date, daily,
  cumulative}``, heatmap rows ``{week_start, days[7]}`` of
  ``{date, amount}``.
"""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import create_db_engine
from app.models import Base
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User
from app.services import dashboard_service

SUMMARY_KEYS = {
    "year_month",
    "total",
    "budget_amount",
    "remaining",
    "percentage",
    "is_over_budget",
    "category_count",
}
CATEGORY_ROW_KEYS = {"category_id", "category_name", "color", "amount", "percentage"}


def _session(tmp_path: Path, name: str) -> tuple[Engine, sessionmaker[Session]]:
    """Create this test's SQLite file/schema and its session factory.

    Args:
        tmp_path: pytest-provided directory for this test's database.
        name: Test-specific file name so no two tests share a file.

    Returns:
        tuple[Engine, sessionmaker[Session]]: Engine plus factory;
        fresh sessions come from the factory, never a shared handle.
    """
    engine: Engine = create_db_engine(f"sqlite:///{(tmp_path / f'{name}.db').as_posix()}")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


def _fixture(
    tmp_path: Path, name: str
) -> tuple[sessionmaker[Session], User, Category, Category]:
    """Persist one user and two of their own categories.

    Args:
        tmp_path: pytest-provided directory.
        name: Database file name for this test.

    Returns:
        tuple: The factory, the user, and two category rows (freshly
            loaded so their ids/attributes survive the commit).
    """
    _, factory = _session(tmp_path, name)
    with factory() as session:
        user = User(email="alice@example.com", username="alice", hashed_password="x")
        session.add(user)
        session.commit()
        food = Category(name="Food", color="#111111", user_id=user.id)
        fun = Category(name="Fun", color="#222222", user_id=user.id)
        session.add_all([food, fun])
        session.commit()
    return factory, user, food, fun


def _add_expense(
    factory: sessionmaker[Session],
    user: User,
    category: Category,
    day: date,
    amount: str,
    created_at: datetime | None = None,
) -> None:
    """Persist one expense row for ``user`` through its own commit.

    Args:
        factory: This test's session factory.
        user: The owning user.
        category: The expense's category (already persisted).
        day: Expense calendar date.
        amount: 2-dp amount string.
        created_at: Optional explicit timestamp for ordering tests.
    """
    with factory() as session:
        expense = Expense(
            user_id=user.id,
            category_id=category.id,
            amount=Decimal(amount),
            currency="USD",
            date=day,
            note=None,
        )
        if created_at is not None:
            expense.created_at = created_at
        session.add(expense)
        session.commit()


def _add_budget(factory: sessionmaker[Session], user: User, year_month: str, amount: str) -> None:
    """Persist one budget row for ``user`` through its own commit.

    Args:
        factory: This test's session factory.
        user: The owning user.
        year_month: ``YYYY-MM`` key.
        amount: 2-dp amount string.
    """
    with factory() as session:
        session.add(Budget(user_id=user.id, year_month=year_month, amount=Decimal(amount)))
        session.commit()


class TestDashboardHelpers:
    """Chapter 6 6.10.7 shared-helper coverage (t19 ac5)."""

    def test_month_range_returns_first_of_month_and_next_month_for_february(
        self, tmp_path: Path
    ) -> None:
        """February's half-open window is (2026-02-01, 2026-03-01)."""
        assert dashboard_service.month_range("2026-02") == (
            date(2026, 2, 1),
            date(2026, 3, 1),
        )

    def test_month_range_walks_the_december_year_boundary_to_january_one(
        self, tmp_path: Path
    ) -> None:
        """December's window ends at January 1 of the NEXT year."""
        assert dashboard_service.month_range("2026-12") == (
            date(2026, 12, 1),
            date(2027, 1, 1),
        )

    def test_add_month_rolls_december_to_january_of_the_next_year(self, tmp_path: Path) -> None:
        """add_month(2026-12-15) lands on 2027-01-01."""
        assert dashboard_service.add_month(date(2026, 12, 15)) == date(2027, 1, 1)
        assert dashboard_service.add_month(date(2026, 5, 31)) == date(2026, 6, 1)

    def test_subtract_months_walks_back_across_the_year_boundary_by_one_month(
        self, tmp_path: Path
    ) -> None:
        """subtract_months(2026-01-31, 1) lands on 2025-12-01."""
        assert dashboard_service.subtract_months(date(2026, 1, 31), 1) == date(2025, 12, 1)
        assert dashboard_service.subtract_months(date(2026, 2, 15), 11) == date(2025, 3, 1)

    def test_to_decimal_quantizes_none_int_float_and_decimal_inputs_to_two_places(
        self, tmp_path: Path
    ) -> None:
        """to_decimal(None/int/float/Decimal) all yield 2-dp Decimals."""
        assert dashboard_service.to_decimal(None) == Decimal("0.00")
        assert dashboard_service.to_decimal(5) == Decimal("5.00")
        assert dashboard_service.to_decimal(1.256) == Decimal("1.26")
        assert dashboard_service.to_decimal(Decimal("7.5")) == Decimal("7.50")
        for value in (None, 5, 1.256, Decimal("7.5")):
            assert dashboard_service.to_decimal(value).as_tuple().exponent == -2


def test_all_four_shared_helpers_are_module_level_callables() -> None:
    """The four Chapter 6 6.10.7 helpers exist and are callable."""
    for name in ("month_range", "add_month", "subtract_months", "to_decimal"):
        helper = getattr(dashboard_service, name)
        assert callable(helper), name


class TestDashboardSummary:
    """get_summary coverage (t19 ac2, REQ-BE-090/091)."""

    def test_empty_month_returns_zero_strings_and_a_null_percentage(
        self, tmp_path: Path
    ) -> None:
        """No rows, no budget: 7 keys, "0.00" money, percentage None."""
        factory, user, _, _ = _fixture(tmp_path, "summary_empty")
        with factory() as session:
            body = dashboard_service.get_summary(session, user, "2026-02")
        assert set(body.keys()) == SUMMARY_KEYS
        assert body["year_month"] == "2026-02"
        assert body["total"] == "0.00"
        assert body["budget_amount"] == "0.00"
        assert body["remaining"] == "0.00"
        assert body["percentage"] is None
        assert body["is_over_budget"] is False
        assert body["category_count"] == 0

    def test_budget_and_expenses_produce_string_money_and_a_62_5_percentage(
        self, tmp_path: Path
    ) -> None:
        """Budget 400 + two expenses totalling 250 -> 62.5 percent."""
        factory, user, food, fun = _fixture(tmp_path, "summary_basic")
        _add_budget(factory, user, "2026-02", "400.00")
        _add_expense(factory, user, food, date(2026, 2, 10), "150.00")
        _add_expense(factory, user, fun, date(2026, 2, 20), "100.00")
        with factory() as session:
            body = dashboard_service.get_summary(session, user, "2026-02")
        assert body["total"] == "250.00"
        assert body["budget_amount"] == "400.00"
        assert body["remaining"] == "150.00"
        assert body["percentage"] == 62.5
        assert isinstance(body["percentage"], float)
        assert body["is_over_budget"] is False
        assert body["category_count"] == 2

    def test_exactly_at_budget_is_percentage_100_and_not_over_budget(
        self, tmp_path: Path
    ) -> None:
        """total == budget > 0: percentage 100.0, flag False."""
        factory, user, food, _ = _fixture(tmp_path, "summary_at_budget")
        _add_budget(factory, user, "2026-02", "250.00")
        _add_expense(factory, user, food, date(2026, 2, 10), "250.00")
        with factory() as session:
            body = dashboard_service.get_summary(session, user, "2026-02")
        assert body["percentage"] == 100
        assert body["is_over_budget"] is False
        assert body["remaining"] == "0.00"

    def test_over_budget_flips_the_flag_and_negates_the_remaining_string(
        self, tmp_path: Path
    ) -> None:
        """total > budget: flag True and remaining is a NEGATIVE string."""
        factory, user, food, _ = _fixture(tmp_path, "summary_over")
        _add_budget(factory, user, "2026-02", "100.00")
        _add_expense(factory, user, food, date(2026, 2, 10), "250.25")
        with factory() as session:
            body = dashboard_service.get_summary(session, user, "2026-02")
        assert body["is_over_budget"] is True
        assert body["remaining"] == "-150.25"
        assert body["percentage"] == 250.2 or body["percentage"] == 250.3

    def test_expenses_outside_the_month_window_never_enter_the_totals(
        self, tmp_path: Path
    ) -> None:
        """Jan 31 and Mar 1 rows are excluded from the February total."""
        factory, user, food, _ = _fixture(tmp_path, "summary_window")
        _add_budget(factory, user, "2026-02", "400.00")
        _add_expense(factory, user, food, date(2026, 1, 31), "99.99")
        _add_expense(factory, user, food, date(2026, 3, 1), "99.99")
        _add_expense(factory, user, food, date(2026, 2, 15), "50.00")
        with factory() as session:
            body = dashboard_service.get_summary(session, user, "2026-02")
        assert body["total"] == "50.00"
        assert body["category_count"] == 1


class TestDashboardByCategory:
    """get_by_category coverage (t19 ac3, REQ-BE-092)."""

    def test_rows_carry_the_five_frozen_keys_and_order_by_amount_descending(
        self, tmp_path: Path
    ) -> None:
        """Rows expose the 5 frozen keys, desc order, resolved name/color."""
        factory, user, food, fun = _fixture(tmp_path, "bycat_basic")
        _add_expense(factory, user, food, date(2026, 2, 10), "30.00")
        _add_expense(factory, user, fun, date(2026, 2, 11), "70.00")
        with factory() as session:
            body = dashboard_service.get_by_category(session, user, "2026-02")
        assert set(body.keys()) == {"year_month", "total", "categories"}
        assert body["total"] == "100.00"
        rows = body["categories"]
        assert len(rows) == 2
        for row in rows:
            assert set(row.keys()) == CATEGORY_ROW_KEYS
            assert isinstance(row["amount"], str)
        assert [row["amount"] for row in rows] == ["70.00", "30.00"]
        assert rows[0]["category_name"] == "Fun"
        assert rows[0]["color"] == "#222222"
        assert rows[0]["category_id"] == str(fun.id)
        assert abs(sum(row["percentage"] for row in rows) - 100.0) < 0.2

    def test_empty_month_returns_an_empty_category_list_and_a_zero_total(
        self, tmp_path: Path
    ) -> None:
        """No expenses: categories == [] and total == "0.00"."""
        factory, user, _, _ = _fixture(tmp_path, "bycat_empty")
        with factory() as session:
            body = dashboard_service.get_by_category(session, user, "2026-02")
        assert body["categories"] == []
        assert body["total"] == "0.00"
        assert body["year_month"] == "2026-02"


class TestDashboardTrend:
    """get_trend coverage (t19 ac3, REQ-BE-093)."""

    def test_six_month_window_anchors_on_the_explicit_today_and_walks_ascending(
        self, tmp_path: Path
    ) -> None:
        """today=2026-02-15, months=6 -> 2025-09 .. 2026-02 ascending."""
        factory, user, food, _ = _fixture(tmp_path, "trend_basic")
        _add_expense(factory, user, food, date(2026, 2, 10), "10.00")
        _add_expense(factory, user, food, date(2025, 11, 3), "5.50")
        with factory() as session:
            body = dashboard_service.get_trend(session, user, 6, today=date(2026, 2, 15))
        months = body["months"]
        assert len(months) == 6
        assert [item["year_month"] for item in months] == [
            "2025-09",
            "2025-10",
            "2025-11",
            "2025-12",
            "2026-01",
            "2026-02",
        ]
        for item in months:
            assert set(item.keys()) == {"year_month", "total"}
        assert months[-1]["total"] == "10.00"
        assert months[2]["total"] == "5.50"

    def test_months_with_no_expenses_are_included_as_zero_strings(
        self, tmp_path: Path
    ) -> None:
        """A month with no rows still appears with total "0.00"."""
        factory, user, _, _ = _fixture(tmp_path, "trend_zeros")
        with factory() as session:
            body = dashboard_service.get_trend(session, user, 6, today=date(2026, 2, 15))
        assert [item["total"] for item in body["months"]] == ["0.00"] * 6

    def test_twelve_month_window_from_february_walks_back_across_the_year_boundary(
        self, tmp_path: Path
    ) -> None:
        """12 months ending 2026-02 starts at 2025-03 (boundary walked)."""
        factory, user, food, _ = _fixture(tmp_path, "trend_year")
        _add_expense(factory, user, food, date(2025, 3, 1), "1.00")
        _add_expense(factory, user, food, date(2024, 12, 31), "99.00")  # outside window
        with factory() as session:
            body = dashboard_service.get_trend(session, user, 12, today=date(2026, 2, 15))
        months = body["months"]
        assert len(months) == 12
        assert months[0]["year_month"] == "2025-03"
        assert months[0]["total"] == "1.00"
        assert months[-1]["year_month"] == "2026-02"
        assert all(item["total"] != "99.00" for item in months)


class TestDashboardCumulative:
    """get_cumulative coverage (t19 ac4, REQ-BE-094)."""

    def test_28_day_february_lists_every_day_and_the_last_cumulative_is_the_total(
        self, tmp_path: Path
    ) -> None:
        """Feb 2026 (28 days): 28 rows, running sum ends at the total."""
        factory, user, food, fun = _fixture(tmp_path, "cum_feb")
        _add_budget(factory, user, "2026-02", "500.00")
        _add_expense(factory, user, food, date(2026, 2, 3), "10.00")
        _add_expense(factory, user, fun, date(2026, 2, 3), "2.50")
        _add_expense(factory, user, food, date(2026, 2, 28), "7.50")
        with factory() as session:
            body = dashboard_service.get_cumulative(session, user, "2026-02")
        days = body["days"]
        assert len(days) == 28
        assert body["budget"] == "500.00"
        assert days[0]["date"] == "2026-02-01"
        assert days[-1]["date"] == "2026-02-28"
        for day in days:
            assert set(day.keys()) == {"date", "daily", "cumulative"}
        assert days[1]["daily"] == "0.00"  # Feb 2 has no expenses
        assert days[2]["daily"] == "12.50"  # Feb 3 combines both rows
        assert days[-1]["cumulative"] == "20.00"

    def test_leap_february_has_29_days(self, tmp_path: Path) -> None:
        """Feb 2028 is a leap February: 29 day rows."""
        factory, user, _, _ = _fixture(tmp_path, "cum_leap")
        with factory() as session:
            body = dashboard_service.get_cumulative(session, user, "2028-02")
        assert len(body["days"]) == 29
        assert body["days"][-1]["date"] == "2028-02-29"

    def test_thirty_one_day_month_has_one_row_per_day(self, tmp_path: Path) -> None:
        """A 31-day month with 3 spend days: 31 rows, 3 non-zero daily."""
        factory, user, food, _ = _fixture(tmp_path, "cum_march")
        for day in (2, 15, 31):
            _add_expense(factory, user, food, date(2026, 3, day), "1.00")
        with factory() as session:
            body = dashboard_service.get_cumulative(session, user, "2026-03")
        days = body["days"]
        assert len(days) == 31
        assert sum(1 for day in days if day["daily"] != "0.00") == 3
        assert days[-1]["cumulative"] == "3.00"


class TestDashboardHeatmap:
    """get_heatmap coverage (t19 ac4, REQ-BE-095)."""

    def test_week_rows_start_on_monday_and_carry_exactly_seven_days(
        self, tmp_path: Path
    ) -> None:
        """today=2026-03-05, weeks=6: first row Monday 2026-01-26."""
        factory, user, food, _ = _fixture(tmp_path, "heat_grid")
        _add_expense(factory, user, food, date(2026, 2, 1), "10.00")
        with factory() as session:
            body = dashboard_service.get_heatmap(session, user, 6, today=date(2026, 3, 5))
        weeks = body["weeks"]
        assert len(weeks) == 6
        assert weeks[0]["week_start"] == "2026-01-26"
        for week in weeks:
            assert set(week.keys()) == {"week_start", "days"}
            assert len(week["days"]) == 7
            for day in week["days"]:
                assert set(day.keys()) == {"date", "amount"}
        first_sunday = weeks[0]["days"][6]
        assert first_sunday["date"] == "2026-02-01"
        assert first_sunday["amount"] == "10.00"
        assert weeks[-1]["days"][-1]["date"] == "2026-03-08"

    def test_missing_days_are_zero_filled_and_max_amount_is_the_daily_peak(
        self, tmp_path: Path
    ) -> None:
        """Days without expenses read "0.00"; max_amount is the day peak."""
        factory, user, food, fun = _fixture(tmp_path, "heat_zero")
        _add_expense(factory, user, food, date(2026, 3, 2), "60.00")
        _add_expense(factory, user, fun, date(2026, 3, 2), "50.00")  # peak day 110.00
        _add_expense(factory, user, food, date(2026, 3, 3), "20.00")
        with factory() as session:
            body = dashboard_service.get_heatmap(session, user, 6, today=date(2026, 3, 5))
        assert body["max_amount"] == "110.00"
        amounts = {day["date"]: day["amount"] for week in body["weeks"] for day in week["days"]}
        assert amounts["2026-03-02"] == "110.00"
        assert amounts["2026-03-04"] == "0.00"
        assert amounts["2026-01-26"] == "0.00"

    def test_a_thirteen_week_window_from_january_crosses_the_year_boundary(
        self, tmp_path: Path
    ) -> None:
        """13 weeks anchored 2026-01-05 start in 2025-10 (boundary)."""
        factory, user, _, _ = _fixture(tmp_path, "heat_year")
        with factory() as session:
            body = dashboard_service.get_heatmap(session, user, 13, today=date(2026, 1, 5))
        weeks = body["weeks"]
        assert len(weeks) == 13
        assert weeks[0]["week_start"] == "2025-10-13"
        assert weeks[0]["days"][0]["date"].startswith("2025-10")
        assert weeks[-1]["days"][-1]["date"] == "2026-01-11"


class TestDashboardRecent:
    """get_recent coverage (t19 ac4, REQ-BE-096)."""

    def test_limit_caps_the_result_at_the_requested_count(self, tmp_path: Path) -> None:
        """12 rows exist, limit=5 -> exactly 5 rows back."""
        factory, user, food, _ = _fixture(tmp_path, "recent_limit")
        for day in range(1, 13):
            _add_expense(factory, user, food, date(2026, 2, day), "1.00")
        with factory() as session:
            rows = dashboard_service.get_recent(session, user, 5)
        assert len(rows) == 5

    def test_order_is_date_descending_then_created_at_descending(self, tmp_path: Path) -> None:
        """Newest date first; same-date ties break on created_at DESC."""
        factory, user, food, _ = _fixture(tmp_path, "recent_order")
        base = datetime(2026, 2, 10, 12, 0, 0)
        _add_expense(factory, user, food, date(2026, 2, 1), "1.00")
        _add_expense(factory, user, food, date(2026, 2, 20), "2.00", created_at=base)
        _add_expense(
            factory, user, food, date(2026, 2, 20), "3.00", created_at=base + timedelta(hours=1)
        )
        with factory() as session:
            rows = dashboard_service.get_recent(session, user, 10)
        assert [row.amount for row in rows] == [Decimal("3.00"), Decimal("2.00"), Decimal("1.00")]
        assert [row.date for row in rows] == [
            date(2026, 2, 20),
            date(2026, 2, 20),
            date(2026, 2, 1),
        ]

    def test_other_users_expenses_are_never_returned(self, tmp_path: Path) -> None:
        """A second user's rows never surface in the caller's list."""
        factory, user, food, _ = _fixture(tmp_path, "recent_isolation")
        with factory() as session:
            other = User(email="bob@example.com", username="bob", hashed_password="x")
            session.add(other)
            session.commit()
            other_category = Category(name="Bobs", color="#333333", user_id=other.id)
            session.add(other_category)
            session.commit()
            other_category_id = other_category.id
            other_id = other.id
        _add_expense(factory, user, food, date(2026, 2, 5), "4.00")
        with factory() as session:
            session.add(
                Expense(
                    user_id=other_id,
                    category_id=other_category_id,
                    amount=Decimal("9.00"),
                    currency="USD",
                    date=date(2026, 2, 6),
                    note=None,
                )
            )
            session.commit()
        with factory() as session:
            rows = dashboard_service.get_recent(session, user, 10)
        assert len(rows) == 1
        assert rows[0].amount == Decimal("4.00")
        assert rows[0].user_id == user.id
        assert uuid.UUID(str(rows[0].id)) == rows[0].id
