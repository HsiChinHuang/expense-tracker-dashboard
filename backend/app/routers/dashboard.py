"""Dashboard endpoints: six read-only GET aggregations (t19).

The router is mounted under ``/api/v1/dashboard`` (issue harness pin —
the phase brief's ``/api/dashboard`` omitted the version segment every
merged router carries) and registered in ``create_app()`` AFTER the
budgets router so OpenAPI lists the merged paths first (issue ac6).

It follows the merged t8/t11/t13/t14 pattern: ``Annotated[T,
Depends(...)]`` DI (ruff B008), thin bodies that delegate every
aggregation to :mod:`app.services.dashboard_service` (plan ruling 3),
and every error rendered ``{detail, code, field}`` through the merged
handlers.

Contract pins (docs/issues/t19.md):

* All six operations are GET-only behind the merged
  ``get_current_user``; an unauthenticated call is the frozen 401
  ``{detail, code, field: null}`` (REQ-API-060).
* ``year_month`` is a REQUIRED query rendered through the merged
  422 ``VALIDATION_ERROR`` handler for every malformed form (pattern
  ``^[0-9]{4}-[0-9]{2}$``) and through the merged
  ``validate_year_month`` (via the service) for the month-VALUE form
  (groom ruling 3).
* ``months`` is ``Query(int)`` bounded ``1..24`` default 6, ``weeks``
  ``1..52`` default 12, ``limit`` ``1..50`` default 10 (Chapter 7
  7.7.3/7.7.5/7.7.6); out-of-range or non-integer values render the
  merged 422 shape before any service code runs (groom ruling 2).
* ``response_model`` is deliberately absent (groom ruling 10): the
  frozen contract is the observable JSON key set the service emits,
  and the ``today=`` determinism kwarg never crosses the wire.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.routers.expenses import _to_response
from app.schemas.dashboard import DashboardRecentResponse
from app.services import dashboard_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

YEAR_MONTH_PATTERN = r"^[0-9]{4}-[0-9]{2}$"
"""year_month query-parameter format (Chapter 7 7.7.1/7.7.2/7.7.4)."""

YearMonthQuery = Annotated[
    str,
    Query(pattern=YEAR_MONTH_PATTERN, description="Month in YYYY-MM form."),
]
"""Required year_month query (missing/malformed -> merged 422)."""


@router.get("/summary")
def get_summary(
    session: SessionDep,
    current_user: CurrentUser,
    year_month: YearMonthQuery,
) -> dict[str, Any]:
    """Return the caller's seven-key monthly summary (REQ-API-061).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller (data is scoped to them).
        year_month: Required ``YYYY-MM`` query (malformed -> 422).

    Returns:
        dict[str, Any]: The frozen seven-key summary body.
    """
    return dashboard_service.get_summary(session, current_user, year_month)


@router.get("/by-category")
def get_by_category(
    session: SessionDep,
    current_user: CurrentUser,
    year_month: YearMonthQuery,
) -> dict[str, Any]:
    """Return the caller's category breakdown for one month (REQ-API-062).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller.
        year_month: Required ``YYYY-MM`` query (malformed -> 422).

    Returns:
        dict[str, Any]: ``{year_month, total, categories}`` with the
            frozen five-key rows ordered amount-descending.
    """
    return dashboard_service.get_by_category(session, current_user, year_month)


@router.get("/trend")
def get_trend(
    session: SessionDep,
    current_user: CurrentUser,
    months: Annotated[int, Query(ge=1, le=24)] = 6,
) -> dict[str, Any]:
    """Return a contiguous ascending month-window trend (REQ-API-063).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller.
        months: Window length, 1..24, default 6 (Chapter 7 7.7.3;
            out-of-range or non-integer -> merged 422).

    Returns:
        dict[str, Any]: ``{months: [{year_month, total}, ...]}``.
    """
    return dashboard_service.get_trend(session, current_user, months)


@router.get("/cumulative")
def get_cumulative(
    session: SessionDep,
    current_user: CurrentUser,
    year_month: YearMonthQuery,
) -> dict[str, Any]:
    """Return one cumulative day row per calendar day (REQ-API-064).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller.
        year_month: Required ``YYYY-MM`` query (malformed -> 422).

    Returns:
        dict[str, Any]: ``{year_month, budget, days}`` with the frozen
            ``{date, daily, cumulative}`` day keys.
    """
    return dashboard_service.get_cumulative(session, current_user, year_month)


@router.get("/heatmap")
def get_heatmap(
    session: SessionDep,
    current_user: CurrentUser,
    weeks: Annotated[int, Query(ge=1, le=52)] = 12,
) -> dict[str, Any]:
    """Return Monday-aligned seven-day heatmap rows (REQ-API-065).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller.
        weeks: Number of weeks, 1..52, default 12 (Chapter 7 7.7.5;
            out-of-range or non-integer -> merged 422).

    Returns:
        dict[str, Any]: ``{max_amount, weeks}`` with zero-filled days.
    """
    return dashboard_service.get_heatmap(session, current_user, weeks)


@router.get("/recent", response_model=DashboardRecentResponse)
def get_recent(
    session: SessionDep,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> DashboardRecentResponse:
    """Return the caller's newest expenses (Chapter 7 7.7.6, REQ-API-065).

    Args:
        session: Request-scoped database session.
        current_user: Authenticated caller (foreign rows never appear).
        limit: Maximum items, 1..50, default 10 (out-of-range or
            non-integer -> merged 422).

    Returns:
        DashboardRecentResponse: ``{items}`` in the merged ten-key
            expense shape (groom ruling 7; the merged ``_to_response``
            helper is reused verbatim).
    """
    expenses = dashboard_service.get_recent(session, current_user, limit)
    return DashboardRecentResponse(items=[_to_response(row) for row in expenses])
