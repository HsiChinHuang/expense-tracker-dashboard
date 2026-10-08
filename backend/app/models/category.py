"""The Category model mapped to the ``categories`` table (REQ-DB-020/021/022).

The model lives on the shared ``Base`` introduced by t6 in
``app/models/user.py``. System categories (``is_system`` TRUE, ``user_id``
NULL) are provisioned by the Alembic data step in revision ``002`` through
``app.scripts.seed`` (REQ-DB-072); the create/update/delete business rules
for them are API-layer concerns owned by t11 (REQ-DB-023).

Documented deviations (Definition-of-Done, per docs/issues/t10.md):

* REQ-DB-021's color CHECK is normally written ``color ~ '^#[0-9A-Fa-f]{6}$'``
  which is PostgreSQL-only (SQLite has no ``~`` operator). The portable
  form below uses string functions only and is probed on SQLite 3.45.1 to
  accept ``#EF4444``/``#abcdef`` and reject ``EF4444``, ``#GGGGGG``,
  ``#12345`` and ``#1234567``. It is defined ONCE here and imported by the
  revision so model and migration cannot drift (REQ-TECH-031).
* REQ-DB-020 asks for TIMESTAMPTZ, but the dev/test engine is SQLite;
  ``sa.DateTime`` + ``server_default=func.now()`` is used exactly as t6's
  ``User`` does (phase_5_infra owns PostgreSQL engine selection).
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base

COLOR_CHECK_SQL = (
    "length(color) = 7 AND substr(color, 1, 1) = '#' "
    "AND rtrim(upper(substr(color, 2)), '0123456789ABCDEF') = ''"
)
"""Portable HEX-color CHECK (REQ-DB-021), shared with revision 002."""

SYSTEM_CONSISTENCY_CHECK_SQL = (
    "(is_system AND user_id IS NULL) "
    "OR (NOT is_system AND user_id IS NOT NULL)"
)
"""System/custom shape CHECK (REQ-DB-021), shared with revision 002."""


class Category(Base):
    """A spending category row (REQ-DB-020/021/022).

    The primary key is generated in Python (REQ-TECH-032, t6 precedent).
    ``user_id`` is NULL exactly for the ten seeded system categories
    (REQ-DB-023 at the model/migration level); the partial unique index
    ``idx_categories_user_name_unique`` excludes those rows so any number
    of users may each own a category of the same name (REQ-DB-022).
    """

    __tablename__ = "categories"
    __table_args__ = (
        sa.CheckConstraint(COLOR_CHECK_SQL, name="ck_categories_color_format"),
        sa.CheckConstraint(
            SYSTEM_CONSISTENCY_CHECK_SQL,
            name="ck_categories_system_consistency",
        ),
        sa.Index("idx_categories_user_id", "user_id"),
        sa.Index("idx_categories_is_system", "is_system"),
        sa.Index(
            "idx_categories_user_name_unique",
            "user_id",
            "name",
            unique=True,
            sqlite_where=sa.text("user_id IS NOT NULL"),
            postgresql_where=sa.text("user_id IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    color: Mapped[str] = mapped_column(sa.String(7), nullable=False)
    icon: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    is_system: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False, server_default=sa.false()
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
