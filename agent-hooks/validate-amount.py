"""Amount guardrail hook (REQ-AI-091, REQ-EXT-020/REQ-EXT-021).

Pure, standard-library-only validation of an expense amount. The rules
mirror the merged backend money rules exactly (the schema/service
ceiling ``AMOUNT_MAX``), so a guardrail decision can never disagree with
the API decision. The module performs no I/O and has no side effects on
import. See agent-hooks/README.md for the trigger points.
"""

from decimal import Decimal, InvalidOperation

MAX_AMOUNT = Decimal("999999999.99")
"""NUMERIC(12,2) capacity ceiling, equal to the merged backend AMOUNT_MAX."""

MAX_DECIMAL_PLACES = 2
"""The money column scale: at most two decimal places."""


def validate_amount(value: object) -> Decimal:
    """Return ``value`` as a valid amount Decimal, or raise ValueError.

    Rules (identical to the merged backend money rules): the value must
    be present, a valid finite number, strictly positive, at most
    ``MAX_AMOUNT``, and carry at most ``MAX_DECIMAL_PLACES`` decimals.

    Args:
        value: The raw amount supplied by the caller (any object).

    Returns:
        Decimal: The validated amount, unchanged in value.

    Raises:
        ValueError: If the amount is missing, non-numeric, zero,
            negative, above the ceiling, or has too many decimals.
    """
    if value is None:
        raise ValueError("amount is required")

    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("amount is required")
        try:
            amount = Decimal(text)
        except InvalidOperation:
            raise ValueError("amount must be a valid number") from None
    elif isinstance(value, bool):
        raise ValueError("amount must be a number, not a boolean")
    elif isinstance(value, int):
        amount = Decimal(value)
    elif isinstance(value, float):
        amount = Decimal(str(value))
    elif isinstance(value, Decimal):
        amount = value
    else:
        raise ValueError("amount must be a number")

    if not amount.is_finite():
        raise ValueError("amount must be a finite number")
    if amount <= 0:
        raise ValueError("amount must be strictly positive")
    if amount > MAX_AMOUNT:
        raise ValueError("amount exceeds the maximum allowed value")

    normalized = amount.normalize()
    exponent = normalized.as_tuple().exponent
    if not isinstance(exponent, int):
        raise ValueError("amount must be a finite number")
    if -exponent > MAX_DECIMAL_PLACES:
        raise ValueError("amount supports at most two decimal places")
    return amount
