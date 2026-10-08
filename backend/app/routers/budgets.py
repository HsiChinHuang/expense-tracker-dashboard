"""Budget endpoints: get / upsert / delete (t14, REQ-API-050..052).

The router is mounted under ``/api/v1/budgets`` and registered in
``create_app()`` AFTER the health, auth, categories and expenses routers
(the merged registration-order precedent, pinned by the OpenAPI node).
It follows the merged t8/t11/t13 pattern: ``Annotated[T, Depends(...)]``
DI (ruff B008), thin bodies that delegate to
:mod:`app.services.budget_service`, and every error rendered
``{detail, code, field}`` through the ``AppError`` handler.

Contract pins (docs/issues/t14.md, review_plan W8):

* ``year_month`` is a PATH parameter carrying the frozen pattern
  ``^[0-9]{4}-[0-9]{2}$``: ALL FOUR malformed forms (``2026-1``,
  ``2026-13``, ``2026-1-01``, ``abcd-ef``) are 422 VALIDATION_ERROR with
  field ``year_month`` through the merged ``RequestValidationError``
  handler on EVERY route here — never 404, never the "0.00" body.
  ``INVALID_MONTH`` is not the wire code on this path (W8).
* Malformed-format != absent: a WELL-FORMED month with no stored row is
  NOT an error — GET answers the exact 200 body
  ``{"year_month": "<echo>", "amount": "0.00"}`` (Chapter 7 7.6.1
  behavior note, REQ-API-050) and persists nothing; DELETE answers 404
  NOT_FOUND (Chapter 7 7.6.3). The two branches never collapse.
* PUT is upsert: 200 for BOTH create and update, NEVER 201
  (REQ-API-051); no route here can answer 403 (ownership misses are
  404/absent in the service, REQ-SEC-031) and no 409 DUPLICATE_BUDGET
  path exists (unreachable under upsert; the DB UNIQUE is the guard).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_client_ip, get_current_user
from app.database import get_db
from app.models.budget import Budget
from app.models.user import User
from app.schemas.budget import (
    YEAR_MONTH_PATTERN,
    BudgetResponse,
    SetBudgetRequest,
)
from app.services import budget_service

router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

YearMonthPath = Annotated[
    str,
    Path(
        pattern=YEAR_MONTH_PATTERN,
        description="Budget month in YYYY-MM form.",
    ),
]
"""Frozen year_month path parameter (Chapter 7 7.6.1/7.6.2, W8)."""


def _to_response(budget: Budget | None, year_month: str) -> BudgetResponse:
    """Build the frozen two-key response, synthesizing the absent case.

    Args:
        budget: The caller's row, or ``None`` for an absent (or
            foreign) month.
        year_month: The path echo (always emitted, REQ-API-050).

    Returns:
        BudgetResponse: Exactly ``{year_month, amount}`` with the
            2-dp-string amount; ``"0.00"`` when no row exists (the
            zero synthesis lives here per the service-shape pin; the
            wire body is frozen by ac3).
    """
    amount = budget.amount if budget is not None else budget_service.ZERO_AMOUNT
    return BudgetResponse(year_month=year_month, amount=amount)


@router.get("/{year_month}", response_model=BudgetResponse)
def get_budget(
    year_month: YearMonthPath,
    session: SessionDep,
    current_user: CurrentUser,
) -> BudgetResponse:
    """Return the caller's budget for one month (REQ-API-050).

    A well-formed but absent month — and any other user's month — is
    the 200 ``amount "0.00"`` body, NEVER 404 (Chapter 7 7.6.1,
    REQ-BE-081, REQ-SEC-030). Malformed formats are 422 (W8).

    Args:
        year_month: ``YYYY-MM`` path (pattern-frozen; malformed -> 422).
        session: Request-scoped database session.
        current_user: Authenticated caller (queries are scoped to them).

    Returns:
        BudgetResponse: The two-key body with the stored or "0.00"
            amount.
    """
    budget = budget_service.get_budget(session, current_user, year_month)
    return _to_response(budget, year_month)


@router.put("/{year_month}", response_model=BudgetResponse)
def set_budget(
    year_month: YearMonthPath,
    body: SetBudgetRequest,
    session: SessionDep,
    current_user: CurrentUser,
    client_ip: Annotated[str | None, Depends(get_client_ip)],
) -> BudgetResponse:
    """Set or update the caller's budget for one month (REQ-API-051).

    Upsert semantics (REQ-BE-080): the FIRST PUT creates and a second
    PUT REPLACES the amount — both answer 200, NEVER 201 — and the
    table keeps exactly one row per (user, month).

    Args:
        year_month: ``YYYY-MM`` path (pattern-frozen; malformed -> 422).
        body: Validated ``{amount}`` payload.
        session: Request-scoped database session.
        current_user: Authenticated caller who owns the row.
        client_ip: Best-effort client IP for the audit row.

    Returns:
        BudgetResponse: The two-key body with the stored amount.

    Raises:
        AppError: 422 INVALID_AMOUNT (field ``amount``) for a bad
            amount VALUE; nothing persists.
    """
    budget = budget_service.set_budget(
        session,
        current_user,
        year_month=year_month,
        amount=body.amount,
        ip_address=client_ip,
    )
    return _to_response(budget, year_month)


@router.delete(
    "/{year_month}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def delete_budget(
    year_month: YearMonthPath,
    session: SessionDep,
    current_user: CurrentUser,
    client_ip: Annotated[str | None, Depends(get_client_ip)],
) -> None:
    """Delete the caller's budget for one month (REQ-API-052).

    Args:
        year_month: ``YYYY-MM`` path (pattern-frozen; malformed -> 422).
        session: Request-scoped database session.
        current_user: Authenticated caller.
        client_ip: Best-effort client IP for the audit row.

    Returns:
        None: 204 with an empty body.

    Raises:
        AppError: 404 NOT_FOUND for absent AND foreign months alike
            (identical bodies, never 403, REQ-SEC-031).
    """
    budget_service.delete_budget(
        session, current_user, year_month=year_month, ip_address=client_ip
    )
    return None
