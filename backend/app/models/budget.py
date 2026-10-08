"""The Budget model mapped to the ``budgets`` table (REQ-DB-040..042).

The model lives on the shared ``Base`` introduced by t6 in
``app/models/user.py``. Amounts are ``Numeric(12, 2)`` bound as
``decimal.Decimal`` end-to-end (REQ-DB-090, REQ-SEC-050); the string
"2000.00" wire form is a serialization concern owned by the schema
layer, never a float. ``year_month`` is a plain ``str`` key end-to-end,
never a date object (REQ-DB-042, REQ-SEC-051).

Documented deviations (Definition-of-Done, per docs/issues/t14.md):

* REQ-DB-040 asks for TIMESTAMPTZ timestamps, but the dev/test engine is
  SQLite; ``sa.DateTime`` + ``server_default=func.now()`` (and
  ``onupdate`` for ``updated_at``) is used exactly as t6's ``User``,
  t12's ``AuditLog`` and t13's ``Expense`` do (phase_5_infra owns
  PostgreSQL engine selection).
* The three constraint SQL strings are defined ONCE here and imported by
  revision 005 so model and migration cannot drift (t10/t12/t13
  precedent, REQ-DB-041). Names are the frozen Chapter 5 5.6.2 set:
  ``uq_budgets_user_month``, ``ck_budgets_amount_positive`` and
  ``ck_budgets_year_month_format``.
* SQLite CHECK emulation — PINNED (review_plan W8/groom): the ``~``
  regex operator does not exist in SQLite, so the format CHECK is the
  GLOB emulation ``year_month GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'``
  — the exact-SQLite emulation of ``^[0-9]{4}-[0-9]{2}$`` (GLOB is
  anchored and case-sensitive by definition). The month-VALUE rule
  (``01..12``; e.g. ``2026-13``) passes this CHECK BY DESIGN: it is not
  DB enforceable this way and is owned by the router/schema pattern
  (W8: ``2026-13`` is a 422 at the wire).
* ``user_id`` cascades with the owner (Chapter 5 5.6.2/5.8: deleting a
  user removes their budgets), provable under ``create_db_engine``'s
  enabled SQLite FKs. The optional ``idx_budgets_user_ym`` (Chapter 5
  5.6.3) is NOT part of the contract and is deliberately absent.
"""

import uuid
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base

AMOUNT_POSITIVE_CHECK_SQL = "amount > 0"
"""Amount CHECK (REQ-DB-041), shared with revision 005."""

YEAR_MONTH_FORMAT_CHECK_SQL = "year_month GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'"
"""year_month format CHECK (REQ-DB-041), shared with revision 005.

The frozen SQLite emulation of ``^[0-9]{4}-[0-9]{2}$``: rejects
``2026-1``, ``abcd-ef``, ``20261-3`` and ``202613``; accepts
``2026-10``. Month VALUES such as ``2026-13`` pass by design — the
month-value rule is API-owned (W8).
"""

UNIQUE_USER_MONTH_NAME = "uq_budgets_user_month"
"""Frozen Chapter 5 5.6.2 name of the UNIQUE constraint (REQ-DB-041)."""

UNIQUE_USER_MONTH_COLUMNS: tuple[str, str] = ("user_id", "year_month")
"""UNIQUE (user_id, year_month) column set (REQ-DB-041/042)."""


class Budget(Base):
    """A monthly spending budget row (REQ-DB-040/041/042).

    One row per (user, month) — the named UNIQUE constraint is the race
    guard behind the PUT upsert contract (REQ-BE-080). ``user_id``
    cascades with the owner; deleting a budget never touches expenses
    (REQ-DB-042: no FK links the two tables).
    """

    __tablename__ = "budgets"
    __table_args__ = (
        sa.UniqueConstraint(
            *UNIQUE_USER_MONTH_COLUMNS, name=UNIQUE_USER_MONTH_NAME
        ),
        sa.CheckConstraint(
            AMOUNT_POSITIVE_CHECK_SQL, name="ck_budgets_amount_positive"
        ),
        sa.CheckConstraint(
            YEAR_MONTH_FORMAT_CHECK_SQL, name="ck_budgets_year_month_format"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    year_month: Mapped[str] = mapped_column(sa.String(7), nullable=False)
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )


__all__ = [
    "AMOUNT_POSITIVE_CHECK_SQL",
    "UNIQUE_USER_MONTH_COLUMNS",
    "UNIQUE_USER_MONTH_NAME",
    "YEAR_MONTH_FORMAT_CHECK_SQL",
    "Budget",
]
