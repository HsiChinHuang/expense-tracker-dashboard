"""SQLAlchemy 2.0 declarative Base and the User model (REQ-DB-010/011).

The declarative ``Base`` is introduced here because t6 is the first
issue with a model; ``Base.metadata`` must contain only the ``users``
table (categories/expenses/budgets/audit_logs are phase_3 scope).

Documented simplifications (Definition-of-Done, per docs/issues/t6.md):

* Email uniqueness is enforced by the database on the *stored* value
  only. Case-insensitive email matching is the service layer's job
  (normalization to lowercase lands with t8, REQ-BE-050); the DB keeps
  a plain UNIQUE on whatever value is stored.
* REQ-DB-010 asks for TIMESTAMPTZ, but the dev/test engine is SQLite,
  where ``sa.DateTime`` stores a naive value and timezone fidelity is
  lost. ``DateTime`` + ``server_default=func.now()`` is used so the
  same DDL works unchanged on PostgreSQL later (phase_5_infra owns
  engine selection and TIMESTAMPTZ fidelity).
"""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models (SQLAlchemy 2.0 style)."""


class User(Base):
    """A user account row mapped to the ``users`` table (REQ-DB-010).

    The primary key is generated in Python (REQ-TECH-032) so UUIDs are
    portable across SQLite and PostgreSQL; ``hashed_password`` holds an
    opaque bcrypt hash produced by t7 — this model never stores or
    derives a plaintext password (REQ-SEC-020).
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        sa.String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        sa.String(50), unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=True, server_default=sa.true()
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
