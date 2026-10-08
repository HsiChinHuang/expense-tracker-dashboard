"""Dashboard aggregation service (t19, REQ-BE-090..096).

Implements Chapter 6 sections 6.10.1..6.10.7 on the merged t13/t14
pattern: aggregation lives HERE (plan ruling 3), the router stays thin,
and every query is scoped to the caller (REQ-SEC-030) with plain
SQLAlchemy ``select()`` only — no database-specific date functions
(plan ruling 4): month windows are half-open ``>= start AND < next``
ranges and all month/day bucketing happens in Python.

Contract pins this module is judged against (docs/issues/t19.md):

* Money is ``decimal.Decimal`` end to end and leaves this module ONLY
  as a 2-decimal string (plan ruling 6, REQ-SEC-050); ``percentage`` is
  the single documented ``float`` conversion (groom ruling 9, Chapter 6
  6.10.1 pseudocode verbatim) and is ``None`` exactly when the budget
  is 0 (REQ-BE-091).
* ``is_over_budget`` is ``total > budget AND budget > 0`` and
  ``remaining`` is ``budget - total`` and MAY BE NEGATIVE (groom
  ruling 4).
* ``year_month`` validity is delegated to the merged
  :func:`app.services.budget_service.validate_year_month` (groom
  ruling 3): the month-VALUE rule renders 422 VALIDATION_ERROR with
  field ``year_month`` through the merged ``AppError`` handler.
* ``get_trend`` and ``get_heatmap`` carry the pinned determinism kwarg
  ``today: date | None = None`` (groom ruling 6, additive to Chapter 6
  6.10.3/6.10.5) so the frozen service tests are clock-independent.
* The wire key sets are the FROZEN issue shapes, which pin the summary
  keys ``total`` / ``budget_amount`` / ``category_count`` and the
  by-category row key ``category_name`` (issue ac1/ac3 — these win over
  the chapter pseudocode names).
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User
from app.services.budget_service import get_budget, validate_year_month

_TWO_DP = Decimal("0.01")
_ZERO = Decimal("0.00")


def month_range(year_month: str) -> tuple[date, date]:
    """Return the half-open ``[first, first-of-next-month)`` window.

    Chapter 6 6.10.7 verbatim; the December boundary walks to
    January 1 of the next year.

    Args:
        year_month: ``YYYY-MM`` key (format already frozen upstream).

    Returns:
        tuple[date, date]: ``(start, end)`` with ``end`` exclusive.
    """
    year, month = (int(part) for part in year_month.split("-"))
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def add_month(d: date) -> date:
    """Return the first day of the month after ``d``'s month.

    Chapter 6 6.10.7 verbatim (December rolls to January next year).

    Args:
        d: Any date inside the anchor month.

    Returns:
        date: The first day of the next month.
    """
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def subtract_months(d: date, n: int) -> date:
    """Return the first day of the month ``n`` months before ``d``'s.

    Chapter 6 6.10.7 verbatim; walks back across year boundaries one
    month at a time.

    Args:
        d: Any date inside the anchor month.
        n: Number of months to walk back (>= 0).

    Returns:
        date: The first day of the target month.
    """
    for _ in range(n):
        if d.month == 1:
            d = date(d.year - 1, 12, 1)
        else:
            d = date(d.year, d.month - 1, 1)
    return d


def to_decimal(value: Any) -> Decimal:
    """Quantize any money-ish value to 2 decimal places.

    Chapter 6 6.10.7 verbatim: ``None`` becomes ``Decimal("0.00")``,
    a ``Decimal`` is quantized, anything else round-trips through
    ``str`` so no binary float ever enters the money path.

    Args:
        value: ``None`` / ``Decimal`` / ``int`` / ``float`` / ``str``.

    Returns:
        Decimal: The 2-decimal quantized value.
    """
    if value is None:
        return _ZERO
    if isinstance(value, Decimal):
        return value.quantize(_TWO_DP)
    return Decimal(str(value)).quantize(_TWO_DP)


def _month_totals(
    session: Session, user: User, start: date, end: date
) -> dict[date, Decimal]:
    """Return the caller's per-day totals inside ``[start, end)``.

    Args:
        session: Active database session.
        user: The caller (every query is scoped to them, REQ-SEC-030).
        start: Window start (inclusive).
        end: Window end (exclusive).

    Returns:
        dict[date, Decimal]: Day -> quantized total (absent = no spend).
    """
    statement = (
        select(Expense.date, func.sum(Expense.amount))
        .where(Expense.user_id == user.id, Expense.date >= start, Expense.date < end)
        .group_by(Expense.date)
    )
    rows: list[Any] = list(session.execute(statement))
    return {row[0]: to_decimal(row[1]) for row in rows}


def _budget_amount(session: Session, user: User, year_month: str) -> Decimal:
    """Return the caller's budget for the month, ``0.00`` when absent.

    Args:
        session: Active database session.
        user: The caller.
        year_month: ``YYYY-MM`` key (already validated).

    Returns:
        Decimal: The stored amount or ``Decimal("0.00")``.
    """
    budget: Budget | None = get_budget(session, user, year_month)
    if budget is None:
        return _ZERO
    return to_decimal(budget.amount)


def get_summary(session: Session, user: User, year_month: str) -> dict[str, Any]:
    """Return the frozen seven-key monthly summary (REQ-BE-090/091).

    Chapter 6 6.10.1 algorithm; the KEY SET is the issue-frozen shape
    ``{year_month, total, budget_amount, remaining, percentage,
    is_over_budget, category_count}`` (issue ac1). Money fields are
    2-dp strings, ``percentage`` is a float or ``None`` (None exactly
    when the budget is 0), ``is_over_budget`` is
    ``total > budget AND budget > 0`` and ``remaining`` may be negative.

    Args:
        session: Active database session.
        user: The caller.
        year_month: ``YYYY-MM`` key.

    Returns:
        dict[str, Any]: The seven-key summary.

    Raises:
        AppError: 422 VALIDATION_ERROR (field ``year_month``) for an
            out-of-range month value (merged validate_year_month).
    """
    validate_year_month(year_month)
    start, end = month_range(year_month)

    total = to_decimal(
        session.scalar(
            select(func.coalesce(func.sum(Expense.amount), 0)).where(
                Expense.user_id == user.id, Expense.date >= start, Expense.date < end
            )
        )
    )
    category_count = int(
        session.scalar(
            select(func.count(func.distinct(Expense.category_id))).where(
                Expense.user_id == user.id, Expense.date >= start, Expense.date < end
            )
        )
        or 0
    )
    budget_amount = _budget_amount(session, user, year_month)

    remaining = budget_amount - total
    percentage = round(float(total / budget_amount * 100), 1) if budget_amount > 0 else None

    return {
        "year_month": year_month,
        "total": str(total),
        "budget_amount": str(budget_amount),
        "remaining": str(remaining),
        "percentage": percentage,
        "is_over_budget": bool(total > budget_amount and budget_amount > 0),
        "category_count": category_count,
    }


def get_by_category(session: Session, user: User, year_month: str) -> dict[str, Any]:
    """Return the frozen three-key category breakdown (REQ-BE-092).

    Chapter 6 6.10.2 algorithm; rows expose the FROZEN five keys
    ``{category_id, category_name, color, amount, percentage}`` (issue
    ac3) ordered amount-descending, amounts are 2-dp strings and the
    empty month yields ``[]`` with total ``"0.00"``.

    Args:
        session: Active database session.
        user: The caller.
        year_month: ``YYYY-MM`` key.

    Returns:
        dict[str, Any]: ``{year_month, total, categories}``.

    Raises:
        AppError: 422 VALIDATION_ERROR for a bad month value.
    """
    validate_year_month(year_month)
    start, end = month_range(year_month)

    statement = (
        select(
            Category.id,
            Category.name,
            Category.color,
            func.sum(Expense.amount).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(Expense.user_id == user.id, Expense.date >= start, Expense.date < end)
        .group_by(Category.id, Category.name, Category.color)
        .order_by(func.sum(Expense.amount).desc())
    )
    rows: list[Any] = list(session.execute(statement))

    amounts = [(row, to_decimal(row[3])) for row in rows]
    grand_total = sum((amount for _, amount in amounts), _ZERO) or _ZERO

    categories: list[dict[str, Any]] = []
    for row, amount in amounts:
        percentage = float(amount / grand_total * 100) if grand_total > 0 else 0.0
        categories.append(
            {
                "category_id": str(row[0]),
                "category_name": row[1],
                "color": row[2],
                "amount": str(amount),
                "percentage": round(percentage, 1),
            }
        )

    return {"year_month": year_month, "total": str(grand_total), "categories": categories}


def get_trend(
    session: Session, user: User, months: int, today: date | None = None
) -> dict[str, Any]:
    """Return ``months`` contiguous ascending month buckets (REQ-BE-093).

    Chapter 6 6.10.3: the window ENDS at the current month, bucketing is
    done in Python (plan ruling 4), months with no expenses appear as
    ``"0.00"``, and items carry exactly ``{year_month, total}`` (issue
    ac3, no label). ``today`` is the pinned determinism kwarg (groom
    ruling 6).

    Args:
        session: Active database session.
        user: The caller.
        months: Window length, 1..24 (bounds enforced by the router).
        today: Anchor day (default ``date.today()``).

    Returns:
        dict[str, Any]: ``{months: [{year_month, total}, ...]}``.
    """
    anchor = today or date.today()
    start_month = subtract_months(anchor.replace(day=1), months - 1)

    statement = select(Expense.date, Expense.amount).where(
        Expense.user_id == user.id, Expense.date >= start_month
    )
    buckets: dict[str, Decimal] = {}
    for row in session.execute(statement):
        key = row[0].isoformat()[:7]
        buckets[key] = buckets.get(key, _ZERO) + to_decimal(row[1])

    result: list[dict[str, Any]] = []
    current = start_month
    for _ in range(months):
        key = f"{current.year:04d}-{current.month:02d}"
        result.append({"year_month": key, "total": str(buckets.get(key, _ZERO))})
        current = add_month(current)

    return {"months": result}


def get_cumulative(session: Session, user: User, year_month: str) -> dict[str, Any]:
    """Return one row per calendar day with a running total (REQ-BE-094).

    Chapter 6 6.10.4: every day of the month (28/29/31) is emitted,
    missing days are ``"0.00"``, and the day object keys are the FROZEN
    service shape ``{date, daily, cumulative}`` (issue contract
    correction — NOT ``daily_total``).

    Args:
        session: Active database session.
        user: The caller.
        year_month: ``YYYY-MM`` key.

    Returns:
        dict[str, Any]: ``{year_month, budget, days}``.

    Raises:
        AppError: 422 VALIDATION_ERROR for a bad month value.
    """
    validate_year_month(year_month)
    start, end = month_range(year_month)
    daily_map = _month_totals(session, user, start, end)
    budget_amount = _budget_amount(session, user, year_month)

    days: list[dict[str, Any]] = []
    cumulative = _ZERO
    current = start
    while current < end:
        daily = daily_map.get(current, _ZERO)
        cumulative += daily
        days.append(
            {
                "date": current.isoformat(),
                "daily": str(daily),
                "cumulative": str(cumulative),
            }
        )
        current += timedelta(days=1)

    return {"year_month": year_month, "budget": str(budget_amount), "days": days}


def get_heatmap(
    session: Session, user: User, weeks: int, today: date | None = None
) -> dict[str, Any]:
    """Return ``weeks`` Monday-aligned seven-day rows (REQ-BE-095).

    Chapter 6 6.10.5 verbatim: the window ends on the Sunday of the
    current week, the first row starts on a Monday, missing days are
    zero-filled, and ``max_amount`` is the DAILY peak (a 2-dp string).
    ``today`` is the pinned determinism kwarg (groom ruling 6).

    Args:
        session: Active database session.
        user: The caller.
        weeks: Number of weeks, 1..52 (bounds enforced by the router).
        today: Anchor day (default ``date.today()``).

    Returns:
        dict[str, Any]: ``{max_amount, weeks: [{week_start, days}]}``.
    """
    anchor = today or date.today()
    end = anchor + timedelta(days=6 - anchor.weekday())
    start = end - timedelta(weeks=weeks, days=-1)
    start = start - timedelta(days=start.weekday())

    statement = (
        select(Expense.date, func.sum(Expense.amount))
        .where(Expense.user_id == user.id, Expense.date >= start, Expense.date <= end)
        .group_by(Expense.date)
    )
    daily_map: dict[date, Decimal] = {}
    for row in session.execute(statement):
        daily_map[row[0]] = to_decimal(row[1])

    max_amount = max(daily_map.values(), default=_ZERO)

    week_list: list[dict[str, Any]] = []
    current = start
    for _ in range(weeks):
        days = [
            {
                "date": (current + timedelta(days=offset)).isoformat(),
                "amount": str(daily_map.get(current + timedelta(days=offset), _ZERO)),
            }
            for offset in range(7)
        ]
        week_list.append({"week_start": current.isoformat(), "days": days})
        current += timedelta(days=7)

    return {"max_amount": str(max_amount), "weeks": week_list}


def get_recent(session: Session, user: User, limit: int) -> list[Expense]:
    """Return the caller's newest expenses (REQ-BE-096).

    Chapter 6 6.10.6 verbatim: ordered ``date DESC, created_at DESC``,
    capped at ``limit`` (1..50, bounds enforced by the router); the
    ROUTER renders the merged ten-key expense shape (groom ruling 7).

    Args:
        session: Active database session.
        user: The caller (foreign rows are unselectable, REQ-SEC-030).
        limit: Maximum number of rows.

    Returns:
        list[Expense]: Rows with their category relationship available.
    """
    statement = (
        select(Expense)
        .where(Expense.user_id == user.id)
        .order_by(Expense.date.desc(), Expense.created_at.desc())
        .limit(limit)
    )
    return list(session.scalars(statement).all())


__all__ = [
    "add_month",
    "get_by_category",
    "get_cumulative",
    "get_heatmap",
    "get_recent",
    "get_summary",
    "get_trend",
    "month_range",
    "subtract_months",
    "to_decimal",
]
