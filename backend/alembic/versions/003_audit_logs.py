"""Audit logs: create the audit_logs table (REQ-DB-050..054).

Hand-written revision (no autogenerate). It creates ONLY the
``audit_logs`` table (plus its two named CHECK constraints and its three
REQ-DB-052 indexes). No data step exists: audit rows are written only by
``app.audit.logger.write_audit_log`` inside business transactions, and
no read/API path exists for this table (FR-AUD-2).

Documented deviations (Definition-of-Done, per docs/issues/t12.md):

* The CHECK SQL and the JSONB/JSON variant are imported from
  ``app.models.audit_log`` so model and migration cannot drift (the t10
  precedent; REQ-DB-054, review_plan W5).
* Timestamps use ``DateTime`` + ``CURRENT_TIMESTAMP`` instead of
  TIMESTAMPTZ so the same DDL works on SQLite (dev/test); PostgreSQL
  engine selection is phase_5_infra scope (t6/t10 precedent).
* ``user_id`` FK has NO ON DELETE CASCADE (Chapter 6 6.11.2 preserve-on-
  user-delete); ``entity_id`` is NOT NULL with no FK (review_plan W5).
* ``downgrade()`` drops the three indexes and the table completely.
"""

import sqlalchemy as sa

from alembic import op
from app.models.audit_log import (
    ACTION_CHECK_SQL,
    ENTITY_TYPE_CHECK_SQL,
    JSONType,
)

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ``audit_logs`` with its named CHECKs and three indexes."""
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=10), nullable=False),
        sa.Column("entity_type", sa.String(length=20), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("old_value", JSONType, nullable=True),
        sa.Column("new_value", JSONType, nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.CheckConstraint(ACTION_CHECK_SQL, name="ck_audit_action"),
        sa.CheckConstraint(
            ENTITY_TYPE_CHECK_SQL, name="ck_audit_entity_type"
        ),
    )
    op.create_index(
        "idx_audit_user_created",
        "audit_logs",
        ["user_id", sa.text("created_at DESC")],
    )
    op.create_index("idx_audit_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_audit_action", "audit_logs", ["action"])


def downgrade() -> None:
    """Drop the audit_logs indexes and table completely."""
    op.drop_index("idx_audit_action", table_name="audit_logs")
    op.drop_index("idx_audit_entity", table_name="audit_logs")
    op.drop_index("idx_audit_user_created", table_name="audit_logs")
    op.drop_table("audit_logs")
