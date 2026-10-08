"""Expense service: create / list / get / update / delete + audit (t13).

Implements Chapter 6 sections 6.8.1..6.8.6 on the merged t8/t11 pattern:
the service owns the single ``db.commit()`` per request (REQ-ARCH-023)
and the router stays thin. Every failure raises
:class:`~app.core.errors.AppError` so the wire shape is always
``{detail, code, field}`` (REQ-ARCH-024).

Contract pins this module is judged against:

* Amounts are ``decimal.Decimal`` end-to-end; the five amount-VALUE
  cases ("0", "-1", three decimals, over max, "") raise 422
  ``INVALID_AMOUNT`` with field ``amount`` (Chapter 2 2.5.2 verbatim).
  Structural problems never reach here — Pydantic already rendered them
  VALIDATION_ERROR.
* Category writes go through t11's :func:`validate_category_access`
  ONLY (404 CATEGORY_NOT_FOUND, field ``category_id``); no second
  validator exists (Constraints).
* The audit row is written through t12's :func:`write_audit_log` inside
  the SAME transaction as the business write (REQ-ARCH-078). The writer
  is imported UNQUALIFIED at module level — that is the pinned W7 seam
  the integration test monkeypatches.
* The audit payload is the byte-pinned expense shape (review_plan W5):
  exactly ``{amount, date, category_id, note}`` produced by
  :func:`expense_to_dict` (REQ-BE-075, Chapter 6 6.8.6 verbatim).
* Cross-user access is 404 ``NOT_FOUND`` (field ``None``), never 403
  (REQ-SEC-031); every query filters ``user_id`` (REQ-SEC-030).
"""

import uuid
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.audit.logger import write_audit_log
from app.core.errors import INVALID_AMOUNT, VALIDATION_ERROR, AppError
from app.models.expense import Expense
from app.models.user import User
from app.services.category_service import validate_category_access

NOT_FOUND = "NOT_FOUND"
"""Appendix B generic 404 code (t11's local-constant precedent)."""

AMOUNT_MAX = Decimal("999999999.99")
"""NUMERIC(12,2) capacity ceiling (Chapter 5 5.11.2)."""

AMOUNT_MIN = Decimal("0.01")
"""Smallest storable 2-dp positive amount (ck_expenses_amount_positive)."""

_TWO_DP = Decimal("0.01")


def _invalid_amount(raw: str) -> AppError:
    """Build the frozen INVALID_AMOUNT error for ``raw``.

    Args:
        raw: The offending client-supplied amount string.

    Returns:
        AppError: 422 INVALID_AMOUNT with field ``amount``.
    """
    return AppError(422, INVALID_AMOUNT, "Invalid amount", field="amount")


def parse_amount(raw: str) -> Decimal:
    """Convert a client amount string to a storable Decimal (REQ-DB-034).

    The rules mirror the column exactly: the string must parse as a
    finite Decimal, carry at most two decimal places, and lie within
    ``[0.01, 999999999.99]`` (NUMERIC(12,2) capacity; the AC's over-max
    case "10000000000.00" and everything larger are rejected here so no
    value can reach a DB overflow). Every violation is the SAME frozen
    error: 422 INVALID_AMOUNT, field ``amount``.

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


def expense_to_dict(expense: Expense) -> dict[str, object]:
    """Serialize the byte-pinned audit payload for ``expense`` (REQ-BE-075).

    Chapter 6 6.8.6 verbatim and review_plan W5: exactly the four keys
    ``amount`` (string), ``category_id`` (string UUID), ``date``
    (``YYYY-MM-DD`` string) and ``note`` (string or ``None``). The
    amount string is quantized to 2 decimals because SQLite stores
    ``Numeric`` as REAL and a read may hand back ``Decimal('125.5')``.

    Args:
        expense: The row (pre- or post-change) to serialize.

    Returns:
        dict[str, object]: The four-key audit payload.
    """
    return {
        "amount": str(expense.amount.quantize(_TWO_DP)),
        "date": expense.date.isoformat(),
        "category_id": str(expense.category_id),
        "note": expense.note,
    }


def _load_own_expense(session: Session, user: User, expense_id: uuid.UUID) -> Expense:
    """Load ``expense_id`` scoped to ``user`` or raise the frozen 404.

    Args:
        session: Active database session.
        user: The caller.
        expense_id: Path-parameter expense uuid.

    Returns:
        Expense: The caller's row with its category eagerly loaded.

    Raises:
        AppError: 404 NOT_FOUND (field ``None``) for unknown AND
            cross-user ids alike — identical bodies, never 403
            (REQ-SEC-031, Chapter 6 6.8.3).
    """
    statement = (
        select(Expense)
        .options(selectinload(Expense.category))
        .where(Expense.id == expense_id, Expense.user_id == user.id)
    )
    expense = session.scalars(statement).first()
    if expense is None:
        raise AppError(404, NOT_FOUND, "Expense not found")
    return expense


def create_expense(
    session: Session,
    user: User,
    *,
    amount: str,
    category_id: uuid.UUID,
    date: date,
    note: str | None,
    ip_address: str | None = None,
) -> Expense:
    """Create an expense and its CREATE audit row in ONE transaction.

    Chapter 6 6.8.1: validate the category, ``add`` + ``flush`` (id
    without committing), stage the audit row, then a SINGLE ``commit()``
    + ``refresh``. The audit row and the expense therefore appear or
    vanish together (REQ-ARCH-078, REQ-PROD-021).

    Args:
        session: Request-scoped session (the ONE session for the request).
        user: The caller who will own the row.
        amount: Client amount string (validated via :func:`parse_amount`).
        category_id: Category to attach (validated by t11's helper).
        date: Calendar date, timezone-naive by type.
        note: Optional free text (length bound owned by the schema).
        ip_address: Best-effort client IP for the audit row.

    Returns:
        Expense: The persisted row with its category loaded.

    Raises:
        AppError: 422 INVALID_AMOUNT (field ``amount``) or 404
            CATEGORY_NOT_FOUND (field ``category_id``).
    """
    value = parse_amount(amount)
    category = validate_category_access(session, user, category_id)

    expense = Expense(
        user_id=user.id,
        category_id=category.id,
        amount=value,
        currency="USD",
        date=date,
        note=note,
    )
    session.add(expense)
    session.flush()

    write_audit_log(
        db=session,
        user_id=user.id,
        action="CREATE",
        entity_type="expense",
        entity_id=expense.id,
        old_value=None,
        new_value=expense_to_dict(expense),
        ip_address=ip_address,
    )

    session.commit()
    session.refresh(expense)
    _ = expense.category  # populate the joined category for the response
    return expense


def list_expenses(
    session: Session,
    user: User,
    *,
    year_month: str | None = None,
    category_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Expense], int]:
    """Return one page of the caller's expenses plus the total count.

    Every filter is AND-combined and always scoped to ``user_id``
    (REQ-SEC-030). ``year_month`` is applied as a HALF-OPEN month range
    (``date >= start, date < next-month-start``) so the index-friendly
    comparison stays exact. Order is ``date DESC, created_at DESC``
    (Chapter 6 6.8.2). ``total`` counts ALL matches, not the page.

    Args:
        session: Active database session.
        user: The caller.
        year_month: Optional ``YYYY-MM`` filter (format owned by the
            router's query validation).
        category_id: Optional category filter.
        page: 1-based page number.
        page_size: Rows per page.

    Returns:
        tuple[list[Expense], int]: The page and the total match count.
    """
    conditions = [Expense.user_id == user.id]
    if year_month is not None:
        try:
            year, month = int(year_month[:4]), int(year_month[5:7])
            start = date(year, month, 1)
            end = (
                date(year + 1, 1, 1)
                if month == 12
                else date(year, month + 1, 1)
            )
        except ValueError:
            raise AppError(
                422, VALIDATION_ERROR, "Invalid year_month", field="year_month"
            ) from None
        conditions.append(Expense.date >= start)
        conditions.append(Expense.date < end)
    if category_id is not None:
        conditions.append(Expense.category_id == category_id)

    total = int(
        session.scalar(
            select(func.count()).select_from(Expense).where(*conditions)
        )
        or 0
    )
    statement = (
        select(Expense)
        .options(selectinload(Expense.category))
        .where(*conditions)
        .order_by(Expense.date.desc(), Expense.created_at.desc(), Expense.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(session.scalars(statement).all())
    return items, total


def get_expense(session: Session, user: User, expense_id: uuid.UUID) -> Expense:
    """Return the caller's expense or the frozen 404 (REQ-BE-072).

    Args:
        session: Active database session.
        user: The caller.
        expense_id: Path-parameter expense uuid.

    Returns:
        Expense: The caller's row.

    Raises:
        AppError: 404 NOT_FOUND for unknown / cross-user ids.
    """
    return _load_own_expense(session, user, expense_id)


def update_expense(
    session: Session,
    user: User,
    expense_id: uuid.UUID,
    *,
    amount: str | None = None,
    category_id: uuid.UUID | None = None,
    date: date | None = None,
    note: str | None = None,
    note_sent: bool = False,
    ip_address: str | None = None,
) -> Expense:
    """Apply a partial update and its UPDATE audit row atomically.

    Chapter 6 6.8.4: the old payload is captured BEFORE any mutation, a
    CHANGED ``category_id`` is re-validated through t11's helper, the
    fields present in the request are assigned, the audit row carries
    BOTH old and new payloads, and the single commit lands them
    together. A validation failure therefore leaves the row UNCHANGED.

    Args:
        session: Active database session.
        user: The caller.
        expense_id: Path-parameter expense uuid.
        amount: Replacement amount string, or None to keep.
        category_id: Replacement category, or None to keep.
        date: Replacement date, or None to keep.
        note: Replacement note.
        note_sent: Whether the client sent the ``note`` key at all
            (Pydantic cannot distinguish "absent" from "explicit null"
            without ``model_fields_set``, so the router forwards it).
        ip_address: Best-effort client IP for the audit row.

    Returns:
        Expense: The updated row.

    Raises:
        AppError: 404 NOT_FOUND (unknown/cross-user), 404
            CATEGORY_NOT_FOUND (changed invalid category), or 422
            INVALID_AMOUNT (bad amount value).
    """
    expense = _load_own_expense(session, user, expense_id)
    old_value = expense_to_dict(expense)

    if amount is not None:
        expense.amount = parse_amount(amount)
    if category_id is not None and category_id != expense.category_id:
        category = validate_category_access(session, user, category_id)
        expense.category_id = category.id
        expense.category = category
    if date is not None:
        expense.date = date
    if note_sent:
        expense.note = note

    write_audit_log(
        db=session,
        user_id=user.id,
        action="UPDATE",
        entity_type="expense",
        entity_id=expense.id,
        old_value=old_value,
        new_value=expense_to_dict(expense),
        ip_address=ip_address,
    )

    session.commit()
    session.refresh(expense)
    _ = expense.category
    return expense


def delete_expense(
    session: Session,
    user: User,
    expense_id: uuid.UUID,
    ip_address: str | None = None,
) -> None:
    """Delete the caller's expense and its DELETE audit row atomically.

    Chapter 6 6.8.5: the audit row carries ``old_value`` only
    (``new_value`` NULL) and shares the delete's transaction.

    Args:
        session: Active database session.
        user: The caller.
        expense_id: Path-parameter expense uuid.
        ip_address: Best-effort client IP for the audit row.

    Raises:
        AppError: 404 NOT_FOUND for unknown / cross-user ids (the
            victim's row survives untouched).
    """
    expense = _load_own_expense(session, user, expense_id)
    old_value = expense_to_dict(expense)

    write_audit_log(
        db=session,
        user_id=user.id,
        action="DELETE",
        entity_type="expense",
        entity_id=expense.id,
        old_value=old_value,
        new_value=None,
        ip_address=ip_address,
    )

    session.delete(expense)
    session.commit()


__all__ = [
    "create_expense",
    "delete_expense",
    "expense_to_dict",
    "get_expense",
    "list_expenses",
    "parse_amount",
    "update_expense",
]
