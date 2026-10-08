"""The Expense model mapped to the ``expenses`` table (REQ-DB-030..034).

The model lives on the shared ``Base`` introduced by t6 in
``app/models/user.py``. Amounts are ``Numeric(12, 2)`` bound as
``decimal.Decimal`` end-to-end (REQ-DB-090, REQ-SEC-050); the string
"125.50" wire form is a serialization concern owned by the schema layer,
never a float.

Documented deviations (Definition-of-Done, per docs/issues/t13.md):

* REQ-DB-030 asks for TIMESTAMPTZ timestamps, but the dev/test engine is
  SQLite; ``sa.DateTime`` + ``server_default=func.now()`` (and
  ``onupdate`` for ``updated_at``) is used exactly as t6's ``User``,
  t10's ``Category`` and t12's ``AuditLog`` do (phase_5_infra owns
  PostgreSQL engine selection).
* ``date`` is ``sa.Date`` — a plain calendar date with NO timezone
  component (REQ-SEC-051, Chapter 5 5.12.1).
* The two CHECK SQL strings are defined ONCE here and imported by
  revision 004 so model and migration cannot drift (t10/t12 precedent,
  REQ-DB-031). Names are the frozen Chapter 5 5.5.2 set.
* ``note`` <= 500 chars is a schema-layer bound (REQ-DB-034): Chapter 5
  5.5.2 defines exactly two CHECKs for this table and a length CHECK is
  not one of them, so adding a third would drift the frozen constraint
  set. The Pydantic schema enforces the bound on every write path.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.category import Category
from app.models.user import Base

AMOUNT_POSITIVE_CHECK_SQL = "amount > 0"
"""Amount CHECK (REQ-DB-031), shared with revision 004."""

CURRENCY_USD_CHECK_SQL = "currency = 'USD'"
"""Currency CHECK (REQ-DB-031/034), shared with revision 004."""


class Expense(Base):
    """An expense row (REQ-DB-030/032/033).

    ``user_id`` cascades with the owner (deleting a user removes their
    expenses); ``category_id`` RESTRICTs so a category still referenced
    by an expense cannot be deleted at the DB level even if the service
    guard is bypassed (REQ-DB-032). The four REQ-DB-033 indexes carry
    the frozen Chapter 5 5.5.3 names.
    """

    __tablename__ = "expenses"
    __table_args__ = (
        sa.CheckConstraint(AMOUNT_POSITIVE_CHECK_SQL, name="ck_expenses_amount_positive"),
        sa.CheckConstraint(CURRENCY_USD_CHECK_SQL, name="ck_expenses_currency_usd"),
        sa.Index("idx_expenses_user_id", "user_id"),
        sa.Index("idx_expenses_user_date", "user_id", sa.text("date DESC")),
        sa.Index("idx_expenses_user_category", "user_id", "category_id"),
        sa.Index("idx_expenses_category_id", "category_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        sa.String(3), nullable=False, default="USD", server_default="USD"
    )
    date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    note: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    category: Mapped[Category] = relationship("Category")


__all__ = ["AMOUNT_POSITIVE_CHECK_SQL", "CURRENCY_USD_CHECK_SQL", "Expense"]
