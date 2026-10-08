"""The AuditLog model mapped to the ``audit_logs`` table (REQ-DB-050..054).

The model lives on the shared ``Base`` introduced by t6 in
``app/models/user.py``. Audit rows are written exclusively by
``app.audit.logger.write_audit_log`` inside the CALLER's transaction
(REQ-ARCH-078); no read path or API surface exists for this table, ever
(FR-AUD-2).

Documented deviations and pins (Definition-of-Done, per docs/issues/t12.md):

* REQ-DB-050 asks for TIMESTAMPTZ, but the dev/test engine is SQLite;
  ``sa.DateTime`` + ``server_default=func.now()`` is used exactly as t6's
  ``User`` and t10's ``Category`` do (phase_5_infra owns PostgreSQL
  engine selection).
* REQ-DB-054's JSONB-on-PostgreSQL / JSON-on-SQLite requirement is met by
  ``JSONType`` below, defined ONCE in this module and imported by
  revision 003 so model and migration cannot drift (t10 no-drift
  precedent). On SQLite the JSON type stores TEXT; dicts round-trip.
* ``entity_id`` is UUID NOT NULL with NO foreign key (review_plan W5:
  on-tree REQ-DB-050 and Chapter 5 5.7.1 both declare NOT NULL; the
  column references no single table so Chapter 5 declares no FK).
* ``user_id`` FK carries NO ``ondelete="CASCADE"`` (Chapter 6 6.11.2
  "Preserve on user delete | No cascade"): deleting a user with audit
  rows must fail, not silently erase history (REQ-SEC-060).
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base

ACTION_CHECK_SQL = "action IN ('CREATE','UPDATE','DELETE')"
"""Audit-action CHECK (REQ-DB-051), shared with revision 003."""

ENTITY_TYPE_CHECK_SQL = "entity_type IN ('expense','budget')"
"""Entity-type CHECK (REQ-DB-051), shared with revision 003.

Categories are deliberately NOT audited (Chapter 5 5.7, REQ-SEC-062),
so 'category' is not in the allowed set.
"""

JSONType = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
"""JSONB on PostgreSQL, JSON/TEXT elsewhere (REQ-DB-054).

Defined once here and imported by revision 003 (t10 drift-prevention
precedent) so the model and the migration can never disagree.
"""


class AuditLog(Base):
    """One immutable audit row (REQ-DB-050/051/052/053).

    Value-shape direction (Chapter 5 5.7.4/5.7.5, Chapter 12 12.7.2):
    CREATE -> ``old_value`` NULL and ``new_value`` populated; UPDATE ->
    both populated; DELETE -> ``old_value`` populated and ``new_value``
    NULL. Payloads carry amounts/dates/ids/notes only, never secrets
    (REQ-SEC-062).
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        sa.CheckConstraint(ACTION_CHECK_SQL, name="ck_audit_action"),
        sa.CheckConstraint(ENTITY_TYPE_CHECK_SQL, name="ck_audit_entity_type"),
        sa.Index("idx_audit_user_created", "user_id", sa.text("created_at DESC")),
        sa.Index("idx_audit_entity", "entity_type", "entity_id"),
        sa.Index("idx_audit_action", "action"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, sa.ForeignKey("users.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    entity_type: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, nullable=False)
    old_value: Mapped[dict[str, object] | None] = mapped_column(
        JSONType, nullable=True
    )
    new_value: Mapped[dict[str, object] | None] = mapped_column(
        JSONType, nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(sa.String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
