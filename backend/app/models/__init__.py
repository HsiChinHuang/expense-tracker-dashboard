"""Model package: re-exports the declarative Base and the User model (t6).

Importing the models here ensures ``Base.metadata`` is fully populated
whenever anything imports ``app.models`` (Alembic autogenerate and the
test fixtures both rely on this).
"""

from app.models.user import Base, User

__all__ = ["Base", "User"]
