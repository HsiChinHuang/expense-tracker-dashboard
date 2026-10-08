"""Budgets: create the budgets table (REQ-DB-040..042).

Hand-written revision (no autogenerate). It creates ONLY the
``budgets`` table plus its three named constraints. No data step exists
and no index is added: the optional ``idx_budgets_user_ym`` (Chapter 5
5.6.3) is NOT part of the frozen contract (docs/issues/t14.md).

Documented deviations (Definition-of-Done, per docs/issues/t14.md):

* The two CHECK SQL strings AND the UNIQUE constraint (name + column
  set) are imported from ``app.models.budget`` so model and migration
  cannot drift (the t10/t12/t13 precedent; REQ-DB-041). The format
  CHECK is the pinned SQLite GLOB emulation of ``^[0-9]{4}-[0-9]{2}$``;
  month VALUES such as ``2026-13`` pass it by design (W8: the
  month-value rule is API-owned).
* Timestamps use ``DateTime`` + ``CURRENT_TIMESTAMP`` (and ``updated_at``
  mirrors ``created_at``) instead of TIMESTAMPTZ so the same DDL works on
  SQLite (dev/test); PostgreSQL engine selection is phase_5_infra scope
  (t6/t10/t12/t13 precedent).
* ``year_month`` is a length-7 ``String`` per the AC pin (Chapter 5
  5.6.1's CHAR(7) rendered as VARCHAR so the ORM ``String(7)`` model and
  the DDL cannot drift — a plain string key, never a date object
  (REQ-DB-042, REQ-SEC-051).
* FK ``user_id`` -> ``users.id`` ON DELETE CASCADE (Chapter 5 5.6.2 and
  the 5.8 FK table): deleting a user removes their budgets.
* ``downgrade()`` drops the table completely.
"""

import sqlalchemy as sa

from alembic import op
from app.models.budget import (
    AMOUNT_POSITIVE_CHECK_SQL,
    UNIQUE_USER_MONTH_COLUMNS,
    UNIQUE_USER_MONTH_NAME,
    YEAR_MONTH_FORMAT_CHECK_SQL,
)

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ``budgets`` with its three named constraints."""
    op.create_table(
        "budgets",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("year_month", sa.String(length=7), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
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


def downgrade() -> None:
    """Drop the budgets table completely."""
    op.drop_table("budgets")
