"""Initial schema: create the users table (REQ-DB-010, REQ-SEC-052).

Hand-written revision (no autogenerate). The ``users`` table is the
only table in this revision; the phase_3 tables (categories, expenses,
budgets, audit_logs) deliberately do not appear here.

Documented simplifications (Definition-of-Done, per docs/issues/t6.md):

* Email uniqueness is a plain UNIQUE on the stored value; lowercase
  normalization is the service layer's job (t8, REQ-BE-050).
* Timestamps use ``DateTime`` + ``CURRENT_TIMESTAMP`` instead of
  TIMESTAMPTZ so the same DDL works on SQLite (dev/test) and
  PostgreSQL; SQLite's CURRENT_TIMESTAMP has 1 s resolution.

The ``is_active``, ``created_at`` and ``updated_at`` columns carry
server-side defaults so a raw (ORM-free) INSERT that supplies only
id/email/username/hashed_password succeeds. The ``id`` column has NO
server default: UUIDs are generated in Python for portability
(REQ-TECH-032; ``gen_random_uuid()`` is forbidden).
"""

import sqlalchemy as sa

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the users table with the Chapter 5 section 5.3.1 shape."""
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
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
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_index("ix_users_email", "users", ["email"])


def downgrade() -> None:
    """Drop the users table (and its index) completely."""
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
