"""Model package: re-exports the declarative Base and the ORM models.

Importing the models here ensures ``Base.metadata`` is fully populated
whenever anything imports ``app.models`` (Alembic autogenerate and the
test fixtures both rely on this). t6 registers ``User``; t10 adds
``Category``; t12 adds ``AuditLog``.
"""

from app.models.audit_log import AuditLog
from app.models.category import Category
from app.models.user import Base, User

__all__ = ["AuditLog", "Base", "Category", "User"]
