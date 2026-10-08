"""Model package: re-exports the declarative Base and the ORM models.

Importing the models here ensures ``Base.metadata`` is fully populated
whenever anything imports ``app.models`` (Alembic autogenerate and the
test fixtures both rely on this). t6 registers ``User``; t10 adds
``Category``; t12 adds ``AuditLog``; t13 adds ``Expense``; t14 adds
``Budget``.
"""

from app.models.audit_log import AuditLog
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import Base, User

__all__ = ["AuditLog", "Base", "Budget", "Category", "Expense", "User"]
