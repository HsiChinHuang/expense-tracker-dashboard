"""Budget service: upsert / get / delete + audit (t14, REQ-BE-080..083).

Implements Chapter 6 sections 6.9.1..6.9.4 on the merged t13 pattern:
the service owns the single ``db.commit()`` per request (REQ-ARCH-023)
and the router stays thin. Every failure raises
:class:`~app.core.errors.AppError` so the wire shape is always
``{detail, code, field}`` (REQ-ARCH-024).

Contract pins this module is judged against:

* ``set_budget`` is a SELECT-then-UPDATE-or-INSERT upsert in ONE
  transaction (Chapter 6 6.9.1, REQ-BE-080): the caller's row for the
  month is loaded; present -> capture the old payload, assign the new
  amount, flush, audit UPDATE (old+new); absent -> add + flush, audit
  CREATE (old NULL). Exactly one ``commit()`` + ``refresh`` either way;
  the DB UNIQUE constraint is the race guard (W9: no retry / ON CONFLICT
  machinery here).
* Amounts are ``decimal.Decimal`` end-to-end; the five amount-VALUE
  cases ("0", "-1", three decimals, over max, "") raise 422
  ``INVALID_AMOUNT`` with field ``amount`` (Chapter 2 2.5.3, mirroring
  t13's frozen split). Structural problems never reach here — Pydantic
  already rendered them VALIDATION_ERROR.
* ``get_budget`` returns the row or ``None`` (REQ-BE-081); the ROUTER
  renders the absent case as the frozen 200 ``amount "0.00"`` body
  (Chapter 7 7.6.1 behavior note). A foreign month reads as ABSENT —
  there is no cross-user 404 state for GET (REQ-SEC-030/031).
* ``delete_budget`` raises 404 ``NOT_FOUND`` (field ``None``) when the
  caller has no row for the month — identical body for absent and
  foreign months, never 403 (REQ-SEC-031) — otherwise writes the DELETE
  audit row (old payload, new NULL) inside the same transaction as the
  delete, then commits once (Chapter 6 6.9.3: audit before commit).
* The audit row is written through t12's :func:`write_audit_log` inside
  the SAME transaction as the business write (REQ-ARCH-078). The writer
  is imported UNQUALIFIED at module level (Chapter 6 6.9.1 calls it
  that way) — that is the pinned W7 seam the integration test
  monkeypatches.
* The audit payload is the byte-pinned budget shape (review_plan W5):
  exactly ``{amount, year_month}``, both strings, produced by
  :func:`budget_to_dict` (Chapter 6 6.9.4 verbatim, REQ-BE-075-parallel).
* ``year_month`` is a plain ``str`` key end-to-end, never a date object
  (REQ-DB-042, REQ-SEC-051). The frozen wire behavior for MALFORMED
  formats is the router/schema-level 422 (W8); :func:`validate_year_month`
  below is Chapter 6 6.9.4's service helper and does NOT change it.
"""

import re
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import write_audit_log
from app.core.errors import INVALID_AMOUNT, VALIDATION_ERROR, AppError
from app.models.budget import Budget
from app.models.user import User

NOT_FOUND = "NOT_FOUND"
"""Appendix B generic 404 code (t11/t13 local-constant precedent)."""

AMOUNT_MAX = Decimal("999999999.99")
"""NUMERIC(12,2) capacity ceiling (Chapter 5 5.11.2, t13 tie-break)."""

AMOUNT_MIN = Decimal("0.01")
"""Smallest storable 2-dp positive amount (ck_budgets_amount_positive)."""

ZERO_AMOUNT = Decimal("0.00")
"""The frozen absent-month synthesis (Chapter 7 7.6.1, REQ-API-050)."""

_TWO_DP = Decimal("0.01")

_YEAR_MONTH_RE = re.compile(r"^[0-9]{4}-[0-9]{2}$")
"""Chapter 6 6.9.4's format rule (mirrors the frozen path pattern)."""


def _invalid_amount(raw: str) -> AppError:
    """Build the frozen INVALID_AMOUNT error for ``raw``.

    Args:
        raw: The offending client-supplied amount string.

    Returns:
        AppError: 422 INVALID_AMOUNT with field ``amount``.
    """
    return AppError(422, INVALID_AMOUNT, "Invalid amount", field="amount")


def validate_year_month(year_month: str) -> str:
    """Return ``year_month`` when it is a real ``YYYY-MM`` month (REQ-BE-083).

    Chapter 6 6.9.4's service helper, and the owner of the MONTH-VALUE
    rule that neither the DB GLOB CHECK nor the path pattern can
    express: ``2026-13`` matches ``^[0-9]{4}-[0-9]{2}$`` (and passes the
    DB CHECK by design), so the ``01..12`` rule is enforced HERE on
    every service entry point. The rendered error is the SAME frozen
    body the merged ``RequestValidationError`` handler produces for the
    pattern failures — 422 VALIDATION_ERROR, field ``year_month``
    (review_plan W8; one frozen expectation per form, never
    ``INVALID_MONTH``, never 404, never the "0.00" body).

    Args:
        year_month: Candidate ``YYYY-MM`` string.

    Returns:
        str: The unchanged input.

    Raises:
        AppError: 422 VALIDATION_ERROR (field ``year_month``) for a
            format violation or an out-of-range month value.
    """
    valid = bool(_YEAR_MONTH_RE.match(year_month))
    if valid:
        try:
            date(int(year_month[:4]), int(year_month[5:7]), 1)
        except ValueError:
            valid = False
    if not valid:
        raise AppError(422, VALIDATION_ERROR, "Invalid year_month", field="year_month")
    return year_month


def parse_amount(raw: str) -> Decimal:
    """Convert a client amount string to a storable Decimal (REQ-BE-083).

    Mirrors t13's :func:`app.services.expense_service.parse_amount`
    exactly: the string must parse as a finite Decimal, carry at most
    two decimal places, and lie within ``[0.01, 999999999.99]``
    (NUMERIC(12,2) capacity; the pinned over-max case "10000000000.00"
    and everything larger are rejected here so no value can reach a DB
    overflow). Every violation is the SAME frozen error: 422
    INVALID_AMOUNT, field ``amount``.

    Args:
        raw: The request-supplied amount string.

    Returns:
        Decimal: The validated amount, quantized to 2 decimal places.

    Raises:
        AppError: 422 INVALID_AMOUNT (field ``amount``) for empty,
            unparseable, non-finite, 3+-decimal, zero, negative, or
            over-capacity values.
    """
    try:
        with localcontext() as ctx:
            ctx.prec = 40
            value = Decimal(raw.strip())
    except InvalidOperation:
        raise _invalid_amount(raw) from None
    if not value.is_finite():
        raise _invalid_amount(raw)
    try:
        with localcontext() as ctx:
            ctx.prec = 40
            quantized = value.quantize(_TWO_DP)
    except InvalidOperation:
        raise _invalid_amount(raw) from None
    if quantized != value or quantized < AMOUNT_MIN or quantized > AMOUNT_MAX:
        raise _invalid_amount(raw)
    return quantized


def budget_to_dict(budget: Budget) -> dict[str, object]:
    """Serialize the byte-pinned audit payload for ``budget`` (W5).

    Chapter 6 6.9.4 verbatim and review_plan W5: exactly the two keys
    ``amount`` (2-dp string) and ``year_month`` (string). The amount
    string is quantized to 2 decimals because SQLite stores ``Numeric``
    as REAL and a read may hand back ``Decimal('2000.5')``.

    Args:
        budget: The row (pre- or post-change) to serialize.

    Returns:
        dict[str, object]: The two-key audit payload.
    """
    return {
        "amount": str(budget.amount.quantize(_TWO_DP)),
        "year_month": budget.year_month,
    }


def _load_own_budget(session: Session, user: User, year_month: str) -> Budget | None:
    """Load the caller's budget row for ``year_month`` (no raise).

    Args:
        session: Active database session.
        user: The caller.
        year_month: ``YYYY-MM`` month key (format already frozen).

    Returns:
        Budget | None: The caller's row, or ``None`` when absent —
            a foreign month reads as ABSENT (REQ-SEC-030: every query
            filters ``user_id``).
    """
    statement = select(Budget).where(
        Budget.user_id == user.id, Budget.year_month == year_month
    )
    return session.scalars(statement).first()


def set_budget(
    session: Session,
    user: User,
    *,
    year_month: str,
    amount: str,
    ip_address: str | None = None,
) -> Budget:
    """Upsert the caller's budget for one month in ONE transaction.

    Chapter 6 6.9.1 / REQ-BE-080: SELECT the caller's row for the month;
    present -> capture the old payload, assign the new amount, audit
    UPDATE (old+new); absent -> add + flush, audit CREATE (old NULL).
    The single ``commit()`` + ``refresh`` lands business write and audit
    row together (REQ-ARCH-078); no duplicate row can appear because the
    named UNIQUE constraint guards the pair (W9: static guard only, no
    retry/ON CONFLICT machinery).

    Args:
        session: Request-scoped session (the ONE session for the request).
        user: The caller who owns the row.
        year_month: ``YYYY-MM`` month key from the PATH (format already
            frozen at the router/schema level, W8).
        amount: Client amount string (validated via :func:`parse_amount`).
        ip_address: Best-effort client IP for the audit row.

    Returns:
        Budget: The persisted row (created or updated).

    Raises:
        AppError: 422 INVALID_AMOUNT (field ``amount``) for a bad
            amount VALUE. A failed validation therefore persists
            NOTHING (the commit is never reached).
    """
    validate_year_month(year_month)
    value = parse_amount(amount)

    budget = _load_own_budget(session, user, year_month)
    if budget is not None:
        old_value = budget_to_dict(budget)
        budget.amount = value
        session.flush()
        write_audit_log(
            db=session,
            user_id=user.id,
            action="UPDATE",
            entity_type="budget",
            entity_id=budget.id,
            old_value=old_value,
            new_value=budget_to_dict(budget),
            ip_address=ip_address,
        )
    else:
        budget = Budget(user_id=user.id, year_month=year_month, amount=value)
        session.add(budget)
        session.flush()
        write_audit_log(
            db=session,
            user_id=user.id,
            action="CREATE",
            entity_type="budget",
            entity_id=budget.id,
            old_value=None,
            new_value=budget_to_dict(budget),
            ip_address=ip_address,
        )

    session.commit()
    session.refresh(budget)
    return budget


def get_budget(session: Session, user: User, year_month: str) -> Budget | None:
    """Return the caller's budget for ``year_month`` or ``None``.

    REQ-BE-081: absence is NOT an error — the ROUTER renders ``None`` as
    the frozen 200 body with ``amount "0.00"`` (Chapter 7 7.6.1 behavior
    note, REQ-API-050). A budget belonging to another user reads as
    ABSENT for the caller (REQ-SEC-030); GET has no cross-user 404
    state by contract.

    Args:
        session: Active database session.
        user: The caller.
        year_month: ``YYYY-MM`` month key (format frozen at the router).

    Returns:
        Budget | None: The caller's row, or ``None``.

    Raises:
        AppError: 422 VALIDATION_ERROR (field ``year_month``) for an
            out-of-range month VALUE such as ``2026-13`` (W8: the
            month-value rule is service-owned; the path pattern already
            rejected the other malformed forms before this runs).
    """
    validate_year_month(year_month)
    return _load_own_budget(session, user, year_month)


def delete_budget(
    session: Session,
    user: User,
    *,
    year_month: str,
    ip_address: str | None = None,
) -> None:
    """Delete the caller's budget for one month and its audit row.

    Chapter 6 6.9.3 / REQ-BE-082: the DELETE audit row (old payload, new
    NULL) shares the delete's transaction; the single commit lands both.
    Deleting a budget never touches expenses (REQ-DB-042: no FK links
    the tables).

    Args:
        session: Active database session.
        user: The caller.
        year_month: ``YYYY-MM`` month key from the PATH.
        ip_address: Best-effort client IP for the audit row.

    Raises:
        AppError: 404 NOT_FOUND (field ``None``) when the caller has no
            row for the month — the IDENTICAL body for absent and
            foreign months, never 403 (REQ-SEC-031); the victim's row
            survives untouched. 422 VALIDATION_ERROR (field
            ``year_month``) for an out-of-range month VALUE such as
            ``2026-13`` (W8, service-owned month-value rule).
    """
    validate_year_month(year_month)
    budget = _load_own_budget(session, user, year_month)
    if budget is None:
        raise AppError(404, NOT_FOUND, "Budget not found")
    old_value = budget_to_dict(budget)

    write_audit_log(
        db=session,
        user_id=user.id,
        action="DELETE",
        entity_type="budget",
        entity_id=budget.id,
        old_value=old_value,
        new_value=None,
        ip_address=ip_address,
    )

    session.delete(budget)
    session.commit()


__all__ = [
    "budget_to_dict",
    "delete_budget",
    "get_budget",
    "parse_amount",
    "set_budget",
    "validate_year_month",
]
