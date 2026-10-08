"""Pydantic schemas for the budget endpoints (t14, REQ-API-050..052).

Chapter 7 section 7.6 is the single frozen contract source:

* The public budget representation (7.6.1 ``BudgetResponse``) is EXACTLY
  the two keys ``{year_month, amount}`` — ``year_month`` echoes the path
  (pattern ``^[0-9]{4}-[0-9]{2}$``) and ``amount`` serializes as a
  2-decimal STRING matching ``^[0-9]+\\.[0-9]{2}$`` (REQ-SEC-050:
  Decimal in, string out, never a JSON float). Both keys are always
  emitted, including the absent-month ``"0.00"`` body.
* Set body (7.6.2 ``SetBudgetRequest``): required ``{amount}`` where
  ``amount`` is a STRING (the chapter's ``^[0-9]+(\\.[0-9]{1,2})?$``
  pattern is deliberately NOT a Pydantic constraint — see below); no
  other field exists (``year_month`` comes from the PATH only) and
  unknown keys are rejected 422 by ``extra="forbid"``.

Amount VALUE validation is deliberately NOT a Pydantic constraint (t13
precedent): the five amount-VALUE cases ("0", "-1", 3 decimals, over
max, "") must render 422 ``INVALID_AMOUNT`` (Chapter 2 2.5.3), a code
the merged ``RequestValidationError`` handler cannot emit — enforcing the
chapter pattern in the schema would render "-1"/"1.234"/"" as
VALIDATION_ERROR and collapse the frozen split. The schema therefore
keeps ``amount`` as the chapter's ``str`` and the service performs the
Decimal conversion/range checks (mirroring t13's ``parse_amount``).
Structural failures (missing key, non-string amount, unknown key) stay
with Pydantic and render VALIDATION_ERROR through the merged handler.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer

AMOUNT_MAX = Decimal("999999999.99")
"""NUMERIC(12,2) capacity ceiling (Chapter 5 5.11.2).

The t13 tie-break the Verifier accepted: the column cannot store
anything above 999,999,999.99 (precision 12, scale 2), so the pinned
over-max case "10000000000.00" and every larger value are rejected with
422 INVALID_AMOUNT by the service and no value can slip through to a DB
overflow.
"""

YEAR_MONTH_PATTERN = r"^[0-9]{4}-[0-9]{2}$"
"""year_month path-parameter format (Chapter 7 7.6.1/7.6.2)."""


class SetBudgetRequest(BaseModel):
    """Request body for ``PUT /api/v1/budgets/{year_month}`` (REQ-API-051).

    Attributes:
        amount: Decimal-string such as "2000.00"; the VALUE rules live
            in the service so the error code is INVALID_AMOUNT (the
            chapter pattern is deliberately not enforced here — see the
            module docstring and the t13 precedent).
    """

    model_config = ConfigDict(extra="forbid")

    amount: str


class BudgetResponse(BaseModel):
    """Public budget representation — exactly two fields (REQ-API-050).

    Attributes:
        year_month: The ``YYYY-MM`` path echo (never a date object).
        amount: 2-decimal string form of the Decimal (REQ-SEC-050);
            ``"0.00"`` for a well-formed but absent month.
    """

    year_month: str
    amount: Decimal

    @field_serializer("amount")
    def _serialize_amount(self, amount: Decimal) -> str:
        """Render the amount as the frozen 2-decimal string (REQ-SEC-050).

        SQLite stores ``Numeric`` as REAL so a read can hand back a
        Decimal such as ``Decimal('2000.5')``; quantizing to 0.01 first
        guarantees the ``^[0-9]+\\.[0-9]{2}$`` shape on every platform.

        Args:
            amount: The Decimal held by the row (or the zero synthesis).

        Returns:
            str: The 2-decimal string form, e.g. ``"2000.00"``.
        """
        return str(amount.quantize(Decimal("0.01")))
