"""Model package: re-exports the declarative Base and the ORM models.

Importing the models here ensures ``Base.metadata`` is fully populated
whenever anything imports ``app.models`` (Alembic autogenerate and the
test fixtures both rely on this). t6 registers ``User``; t10 adds
``Category``.
"""

from app.models.category import Category
from app.models.user import Base, User

__all__ = ["Base", "Category", "User"]
