"""Expenses: create the expenses table (REQ-DB-030..034).

Hand-written revision (no autogenerate). It creates ONLY the
``expenses`` table (plus its two named CHECK constraints and its four
REQ-DB-033 indexes). No data step exists.

Documented deviations (Definition-of-Done, per docs/issues/t13.md):

* The two CHECK SQL strings are imported from ``app.models.expense`` so
  model and migration cannot drift (the t10/t12 precedent; REQ-DB-031).
* Timestamps use ``DateTime`` + ``CURRENT_TIMESTAMP`` (and ``updated_at``
  mirrors ``created_at``) instead of TIMESTAMPTZ so the same DDL works on
  SQLite (dev/test); PostgreSQL engine selection is phase_5_infra scope
  (t6/t10/t12 precedent).
* ``date`` is a plain ``Date`` column: calendar date, no timezone
  (REQ-SEC-051).
* FKs: ``user_id`` -> ``users.id`` ON DELETE CASCADE, ``category_id`` ->
  ``categories.id`` ON DELETE RESTRICT (REQ-DB-032). The RESTRICT is
  DB-enforced and provable by a raw delete of a used category.
* ``downgrade()`` drops the four indexes and the table completely.
"""

import sqlalchemy as sa

from alembic import op
from app.models.expense import (
    AMOUNT_POSITIVE_CHECK_SQL,
    CURRENCY_USD_CHECK_SQL,
)

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ``expenses`` with its named CHECKs and four indexes."""
    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            server_default="USD",
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], ondelete="RESTRICT"
        ),
        sa.CheckConstraint(
            AMOUNT_POSITIVE_CHECK_SQL, name="ck_expenses_amount_positive"
        ),
        sa.CheckConstraint(
            CURRENCY_USD_CHECK_SQL, name="ck_expenses_currency_usd"
        ),
    )
    op.create_index("idx_expenses_user_id", "expenses", ["user_id"])
    op.create_index(
        "idx_expenses_user_date", "expenses", ["user_id", sa.text("date DESC")]
    )
    op.create_index("idx_expenses_user_category", "expenses", ["user_id", "category_id"])
    op.create_index("idx_expenses_category_id", "expenses", ["category_id"])


def downgrade() -> None:
    """Drop the expenses indexes and table completely."""
    op.drop_index("idx_expenses_category_id", table_name="expenses")
    op.drop_index("idx_expenses_user_category", table_name="expenses")
    op.drop_index("idx_expenses_user_date", table_name="expenses")
    op.drop_index("idx_expenses_user_id", table_name="expenses")
    op.drop_table("expenses")
