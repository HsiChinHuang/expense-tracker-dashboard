"""Pydantic schemas for the expense endpoints (t13, REQ-API-040..044).

Chapter 7 section 7.5.1 is the single frozen contract source:

* The public expense representation is EXACTLY the ten keys
  ``{id, amount, currency, category_id, category_name, category_color,
  date, note, created_at, updated_at}`` — ``user_id`` is never exposed
  (REQ-SEC-030). ``amount`` serializes as a 2-decimal STRING matching
  ``^[0-9]+\\.[0-9]{2}$`` (REQ-SEC-050: Decimal in, string out, never a
  JSON float); ``date`` is a plain ``YYYY-MM-DD`` date with no timezone
  (REQ-SEC-051).
* The list body is the W6 envelope with EXACTLY the four keys
  ``{items, total, page, page_size}`` (Chapter 7 7.5.1 verbatim; t16's
  frontend type mirrors this one shape).
* Create body (7.5.2): required ``{amount, category_id, date}``,
  optional ``note`` (<= 500). ``currency`` is NOT a client field; the
  service fixes "USD", so a body sending any currency key is rejected
  422 by ``extra="forbid"`` (REQ-PROD-031 "currency != USD").
* Update body (7.5.4): all fields optional with ``minProperties: 1``;
  the empty body {} is a 422 (enforced by the router-level
  ``model_validate`` guard below via an explicit required check).

Amount VALUE validation is deliberately NOT a Pydantic constraint: the
five amount-value cases ("0", "-1", 3 decimals, over max, "") must
render 422 ``INVALID_AMOUNT`` (Chapter 2 2.5.2), a code the merged
``RequestValidationError`` handler cannot emit. The schema therefore
keeps ``amount`` as the chapter's ``str`` and the service performs the
Decimal conversion/range checks, raising ``AppError`` with the pinned
code and field. Structural failures (missing key, malformed date, note
too long, unknown key) stay with Pydantic and render VALIDATION_ERROR
through the merged handler.
"""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

AMOUNT_MAX = Decimal("999999999.99")
"""NUMERIC(12,2) capacity ceiling (Chapter 5 5.11.2).

The AC pins the over-max 422 case at "10000000000.00" (1e10). The
column itself cannot store anything above 999,999,999.99 (precision 12,
scale 2), so the schema rejects at the column capacity — the pinned
1e10 case and every larger value both 422 INVALID_AMOUNT, and no
value can slip through to a DB overflow.
"""

AMOUNT_MIN = Decimal("0.01")
"""Smallest storable 2-dp positive amount (ck_expenses_amount_positive)."""

NOTE_MAX_LENGTH = 500
"""Maximum note length (Chapter 7 7.5.2, REQ-DB-034)."""

YEAR_MONTH_PATTERN = r"^[0-9]{4}-[0-9]{2}$"
"""year_month query filter format (Chapter 7 7.5.1)."""


class CreateExpenseRequest(BaseModel):
    """Request body for ``POST /api/v1/expenses`` (REQ-API-041).

    Attributes:
        amount: Decimal-string such as "125.50" (chapter pattern; the
            value rules live in the service so the error code is
            INVALID_AMOUNT).
        category_id: Category the expense belongs to.
        date: Calendar date, no timezone.
        note: Optional free text, at most 500 characters.
    """

    model_config = ConfigDict(extra="forbid")

    amount: str
    category_id: UUID
    date: date_type
    note: str | None = Field(default=None, max_length=NOTE_MAX_LENGTH)


class UpdateExpenseRequest(BaseModel):
    """Request body for ``PUT /api/v1/expenses/{id}`` (REQ-API-043).

    Every field is optional (Chapter 7 7.5.4) but at least one must be
    present; the router rejects an all-absent body with 422 before the
    service is reached.

    Attributes:
        amount: Replacement amount string (same rules as create).
        category_id: Replacement category (re-validated by the service).
        date: Replacement calendar date.
        note: Replacement note (None clears it when explicitly sent).
    """

    model_config = ConfigDict(extra="forbid")

    amount: str | None = None
    category_id: UUID | None = None
    date: date_type | None = None
    note: str | None = Field(default=None, max_length=NOTE_MAX_LENGTH)


class ExpenseResponse(BaseModel):
    """Public expense representation — exactly ten fields (REQ-API-040).

    Attributes:
        id: Expense UUID (canonical string on the wire).
        amount: 2-decimal string form of the Decimal (REQ-SEC-050).
        currency: Always "USD" (ck_expenses_currency_usd).
        category_id: Owning category UUID string.
        category_name: Denormalized name from the joined category.
        category_color: Denormalized HEX color from the category.
        date: Calendar date (serializes as YYYY-MM-DD).
        note: Free text or None.
        created_at: Creation timestamp.
        updated_at: Last-update timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    currency: str
    category_id: UUID
    category_name: str
    category_color: str
    date: date_type
    note: str | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("amount")
    def _serialize_amount(self, amount: Decimal) -> str:
        """Render the amount as the frozen 2-decimal string (REQ-SEC-050).

        SQLite stores ``Numeric`` as REAL so a read can hand back a
        Decimal such as ``Decimal('125.5')``; quantizing to 0.01 first
        guarantees the ``^[0-9]+\\.[0-9]{2}$`` shape on every platform.

        Args:
            amount: The Decimal held by the row.

        Returns:
            str: The 2-decimal string form, e.g. ``"125.50"``.
        """
        return str(amount.quantize(Decimal("0.01")))


class ExpenseListResponse(BaseModel):
    """Response body for ``GET /api/v1/expenses`` — the W6 envelope.

    Exactly the four Chapter 7 7.5.1 keys; adding or renaming a key is a
    contract break for t16.

    Attributes:
        items: One page of expenses in date DESC, created_at DESC order.
        total: Total number of matching rows across all pages.
        page: The page that was returned (1-based).
        page_size: Requested page size.
    """

    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int
