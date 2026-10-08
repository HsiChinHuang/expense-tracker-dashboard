"""Categories: create the categories table and seed the system rows.

Hand-written revision (no autogenerate). It creates ONLY the
``categories`` table (plus its two CHECK constraints and its three
indexes) and then runs the idempotent system-category seed as a DATA
STEP — the REQ-DB-072 trigger pinned by ac4 of docs/issues/t10.md.

Documented deviations (Definition-of-Done, per docs/issues/t10.md):

* Naming: Chapter 5 section 5.10.2's idealized layout is
  ``001_initial_schema`` (all five tables) + ``002_seed_categories``
  (data only). The merged project ships one incremental revision per
  vertical slice (001 = users only), so this revision is named
  descriptively ``002_categories`` and carries both the DDL and the
  seed data step (review_plan W15b).
* The color CHECK is the portable SQLite/PostgreSQL string-function form
  imported from ``app.models.category`` so model and migration cannot
  drift (see that module's docstring for the rationale).
* Timestamps use ``DateTime`` + ``CURRENT_TIMESTAMP`` instead of
  TIMESTAMPTZ so the same DDL works on SQLite (dev/test); PostgreSQL
  engine selection is phase_5_infra scope.
* ``downgrade()`` drops the three indexes and the table; the seeded
  rows disappear with the table.
"""

import sqlalchemy as sa

from alembic import op
from app.models.category import COLOR_CHECK_SQL, SYSTEM_CONSISTENCY_CHECK_SQL
from app.scripts.seed import seed_system_categories

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ``categories`` and seed the ten system rows (REQ-DB-020/070)."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint(COLOR_CHECK_SQL, name="ck_categories_color_format"),
        sa.CheckConstraint(
            SYSTEM_CONSISTENCY_CHECK_SQL,
            name="ck_categories_system_consistency",
        ),
    )
    op.create_index("idx_categories_user_id", "categories", ["user_id"])
    op.create_index("idx_categories_is_system", "categories", ["is_system"])
    op.create_index(
        "idx_categories_user_name_unique",
        "categories",
        ["user_id", "name"],
        unique=True,
        sqlite_where=sa.text("user_id IS NOT NULL"),
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    seed_system_categories(op.get_bind())


def downgrade() -> None:
    """Drop the categories indexes and table completely."""
    op.drop_index("idx_categories_user_name_unique", table_name="categories")
    op.drop_index("idx_categories_is_system", table_name="categories")
    op.drop_index("idx_categories_user_id", table_name="categories")
    op.drop_table("categories")
