"""Integration tests for the agent guardrail hooks (REQ-EXT-072, REQ-PLAN-061).

The hook modules live outside the backend project at ``agent-hooks/`` and
carry hyphenated file names (pinned by REQ-AI-091/REQ-EXT-021/022), so
they are not import identifiers. This file therefore reaches them through
an importlib file loader — the loader contract is part of the card and no
packaging change is made to the backend project.

The 14 collected node IDs are a frozen contract (7 amount branches, 5
ownership branches, 2 purity/constant branches). ``MAX_AMOUNT`` is
compared against the merged backend ``AMOUNT_MAX`` so the hook layer and
the schema layer can never drift apart silently.
"""

import importlib.util
from decimal import Decimal
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from app.schemas.expense import AMOUNT_MAX

HOOKS_DIR = Path(__file__).resolve().parents[3] / "agent-hooks"


def _load_hook(module_name: str, filename: str) -> Any:
    """Load a hyphenated hook module from agent-hooks/ by path.

    Args:
        module_name: The name to give the loaded module.
        filename: The hyphenated hook file name.

    Returns:
        Any: The executed hook module (Any: attribute access on a
        dynamically loaded module cannot be statically typed).

    Raises:
        RuntimeError: If the module or its loader is unavailable.
    """
    path = HOOKS_DIR / filename
    if not path.is_file():
        raise RuntimeError(f"hook module not found: {path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"hook module has no loader: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


amount_hook: ModuleType = _load_hook("agent_hook_validate_amount", "validate-amount.py")
ownership_hook: ModuleType = _load_hook("agent_hook_validate_ownership", "validate-ownership.py")


def test_amount_rejects_none_and_empty_string() -> None:
    """None and blank strings are missing amounts (REQ-EXT-021)."""
    for bad in (None, "", "   ", "\t\n"):
        with pytest.raises(ValueError):
            amount_hook.validate_amount(bad)


def test_amount_rejects_non_numeric_strings() -> None:
    """Non-numeric and non-finite inputs raise ValueError, not TypeError."""
    for bad in ("abc", "12.3.4", "10,00", "1e", "1.2.3.4", "nan", "inf", "-inf"):
        with pytest.raises(ValueError):
            amount_hook.validate_amount(bad)
    for bad_object in (True, False, [1], {"amount": 1}, object()):
        with pytest.raises(ValueError):
            amount_hook.validate_amount(bad_object)


def test_amount_rejects_negative_amount() -> None:
    """Negative amounts raise ValueError (REQ-EXT-021)."""
    for bad in ("-0.01", "-1", "-999999999.99", -5, -0.5, Decimal("-2.50")):
        with pytest.raises(ValueError):
            amount_hook.validate_amount(bad)


def test_amount_rejects_zero_amount() -> None:
    """Zero is not a valid expense amount (REQ-EXT-021)."""
    for bad in ("0", "0.00", "0.0", 0, 0.0, Decimal("0.00")):
        with pytest.raises(ValueError):
            amount_hook.validate_amount(bad)


def test_amount_rejects_values_above_max_amount() -> None:
    """The ceiling is the merged backend ceiling, inclusive below it."""
    assert amount_hook.validate_amount("999999999.99") == AMOUNT_MAX
    for bad in ("999999999.991", "10000000000.00", "1e12", AMOUNT_MAX + Decimal("0.01"), 1e10):
        with pytest.raises(ValueError):
            amount_hook.validate_amount(bad)


def test_amount_rejects_more_than_two_decimal_places() -> None:
    """The money scale is two decimals; extra precision is refused."""
    for bad in ("1.234", "0.001", "10.105", "999999999.9899", 1.2345, Decimal("7.001")):
        with pytest.raises(ValueError):
            amount_hook.validate_amount(bad)


def test_amount_returns_decimal_for_valid_input() -> None:
    """Valid input of every accepted shape returns a Decimal."""
    for raw, expected in (
        ("12.34", Decimal("12.34")),
        ("0.01", Decimal("0.01")),
        (5, Decimal("5")),
        (7.5, Decimal("7.5")),
        (Decimal("42.00"), Decimal("42.00")),
        ("  8.90  ", Decimal("8.90")),
        ("1000", Decimal("1000")),
    ):
        result = amount_hook.validate_amount(raw)
        assert isinstance(result, Decimal)
        assert result == expected


def test_ownership_raises_when_owner_id_is_none() -> None:
    """A resource with no owner cannot be accessed (REQ-EXT-022)."""
    with pytest.raises(PermissionError):
        ownership_hook.validate_ownership(None, "user-1")


def test_ownership_raises_when_user_id_is_none() -> None:
    """A caller without an identity cannot access a resource (REQ-EXT-022)."""
    with pytest.raises(PermissionError):
        ownership_hook.validate_ownership("user-1", None)


def test_ownership_raises_when_ids_differ() -> None:
    """Cross-user access is refused (REQ-AI-092, REQ-EXT-022)."""
    with pytest.raises(PermissionError):
        ownership_hook.validate_ownership("user-1", "user-2")


def test_ownership_returns_without_error_when_ids_match() -> None:
    """Matching ids pass without raising and without a value."""
    assert ownership_hook.validate_ownership("user-1", "user-1") is None
    assert ownership_hook.validate_ownership(7, 7) is None


def test_ownership_error_type_is_permission_error() -> None:
    """The failure type is PermissionError, not ValueError or KeyError."""
    with pytest.raises(PermissionError):
        ownership_hook.validate_ownership("user-1", "user-2")
    with pytest.raises(PermissionError):
        ownership_hook.validate_ownership(None, None)
    try:
        ownership_hook.validate_ownership(None, "user-1")
    except PermissionError as error:
        assert not isinstance(error, ValueError)
        assert str(error)
    else:
        raise AssertionError("validate_ownership(None, ...) must raise PermissionError")


def test_max_amount_constant_equals_backend_amount_max() -> None:
    """Hook ceiling and merged schema ceiling are the same value (no drift)."""
    assert amount_hook.MAX_AMOUNT == AMOUNT_MAX
    assert isinstance(amount_hook.MAX_AMOUNT, Decimal)
    assert str(amount_hook.MAX_AMOUNT) == "999999999.99"
    assert AMOUNT_MAX == Decimal("999999999.99")


def test_hook_modules_stay_side_effect_free_on_import() -> None:
    """Importing the hooks exposes only their contract, nothing else."""
    amount_names = {name for name in vars(amount_hook) if not name.startswith("__")}
    ownership_names = {name for name in vars(ownership_hook) if not name.startswith("__")}
    assert amount_names == {
        "Decimal",
        "InvalidOperation",
        "MAX_AMOUNT",
        "MAX_DECIMAL_PLACES",
        "validate_amount",
    }
    assert ownership_names == {"validate_ownership"}

    ownership_source = (HOOKS_DIR / "validate-ownership.py").read_text(encoding="utf-8")
    amount_source = (HOOKS_DIR / "validate-amount.py").read_text(encoding="utf-8")
    ownership_imports = [
        line for line in ownership_source.splitlines() if line.startswith(("import ", "from "))
    ]
    amount_imports = [
        line for line in amount_source.splitlines() if line.startswith(("import ", "from "))
    ]
    assert ownership_imports == []
    assert amount_imports
    assert all("decimal" in line for line in amount_imports)

    assert amount_hook.validate_amount("1.00") == Decimal("1.00")
    assert amount_hook.validate_amount("1.00") == Decimal("1.00")
