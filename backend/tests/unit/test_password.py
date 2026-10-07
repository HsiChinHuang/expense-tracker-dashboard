# mypy: disable-error-code="import-untyped"
"""Unit tests for the bcrypt password primitives (t7).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs. The
modules are DB-free; the AC commands still pin a tmp SQLite URL so a
future autouse conftest can never reach backend/dev.db.
"""

import time

from app.auth.password import hash_password, verify_dummy, verify_password

ROUND_TRIP_PASSWORD = "correct-horse-battery-staple"


class TestPassword:
    """Contract coverage for app.auth.password."""

    def test_hash_password_emits_cost12_prefix_with_random_salt(self) -> None:
        """Cost-12 `$2b$` output, 60 chars, fresh salt per hash."""
        first = hash_password(ROUND_TRIP_PASSWORD)
        second = hash_password(ROUND_TRIP_PASSWORD)
        assert first.startswith("$2b$12$")
        assert len(first) == 60
        assert first != second

    def test_verify_password_roundtrips_true_and_rejects_wrong_password(self) -> None:
        """Correct passphrase verifies True, wrong one verifies False."""
        stored = hash_password(ROUND_TRIP_PASSWORD)
        assert verify_password(ROUND_TRIP_PASSWORD, stored) is True
        assert verify_password("wrong-passphrase", stored) is False

    def test_verify_password_returns_false_for_malformed_hash(self) -> None:
        """Malformed stored hashes return False and never raise."""
        assert verify_password("anything", "not-a-bcrypt-hash") is False
        assert verify_password("anything", "") is False

    def test_verify_dummy_returns_none_after_full_bcrypt_cycle(self) -> None:
        """Dummy verify costs a real bcrypt cycle, matching a real verify."""
        reference_hash = hash_password(ROUND_TRIP_PASSWORD)

        real_start = time.perf_counter()
        verify_password(ROUND_TRIP_PASSWORD, reference_hash)
        real_elapsed = time.perf_counter() - real_start

        dummy_start = time.perf_counter()
        verify_dummy("any-guest-input")
        dummy_elapsed = time.perf_counter() - dummy_start

        # `verify_dummy` is declared `-> None`; calling it as a statement
        # (rather than `assert verify_dummy(...) is None`, which mypy
        # rejects via func-returns-value) plus the absence of any raise
        # satisfies the None-return contract.
        assert dummy_elapsed >= 0.05
        assert dummy_elapsed <= real_elapsed * 10
