# Chapter 5: Database Design

## 5.1 Overview

The database stores five entities:

| Table | Purpose |
|---|---|
| users | Authentication and user identity |
| categories | Expense categories (system and custom) |
| expenses | Individual expense records |
| budgets | Monthly total budget per user |
| audit_logs | Audit trail for expense and budget changes |

All tables use UUID primary keys generated in Python, not by the database.
This ensures identical behavior on PostgreSQL and SQLite.

All timestamps use `TIMESTAMPTZ` on PostgreSQL and ISO text on SQLite.
SQLAlchemy handles the conversion.

## 5.2 Entity Relationship Diagram

```
┌─────────────────┐
│     users       │
│─────────────────│
│ id (PK)         │
│ email (UQ)      │
│ username (UQ)   │
│ hashed_password │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴──────────────────────────────┐
    │                                   │
    ▼                                   ▼
┌─────────────────┐            ┌─────────────────┐
│   categories    │            │    budgets      │
│─────────────────│            │─────────────────│
│ id (PK)         │            │ id (PK)         │
│ user_id (FK)    │            │ user_id (FK)    │
│ name            │            │ year_month      │
│ color           │            │ amount          │
│ icon            │            │ created_at      │
│ is_system       │            │ updated_at      │
│ created_at      │            └─────────────────┘
└────────┬────────┘                     │
         │                              │
         │ 1:N                          │
         │                              │
         ▼                              │
┌─────────────────┐                     │
│    expenses     │                     │
│─────────────────│                     │
│ id (PK)         │                     │
│ user_id (FK)    │                     │
│ category_id(FK) │                     │
│ amount          │                     │
│ currency        │                     │
│ date            │                     │
│ note            │                     │
│ created_at      │                     │
│ updated_at      │                     │
└────────┬────────┘                     │
         │                              │
         │                              │
         │ 1:N                          │
         │                              │
         ▼                              ▼
┌─────────────────────────────────────────────┐
│                audit_logs                    │
│─────────────────────────────────────────────│
│ id (PK)                                     │
│ user_id (FK)                                │
│ action (CREATE/UPDATE/DELETE)               │
│ entity_type (expense/budget)                │
│ entity_id                                   │
│ old_value (JSONB)                           │
│ new_value (JSONB)                           │
│ ip_address                                  │
│ created_at                                  │
└─────────────────────────────────────────────┘
```

**Note**: `audit_logs.entity_id` is not a foreign key because it can point
to either `expenses.id` or `budgets.id`, and the referenced row may be
deleted after the audit entry is written.

## 5.3 Table: users

### 5.3.1 Definition

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| id | UUID | PRIMARY KEY | Python-generated | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | - | Login credential |
| username | VARCHAR(50) | UNIQUE, NOT NULL | - | Display name |
| hashed_password | VARCHAR(255) | NOT NULL | - | bcrypt hash |
| is_active | BOOLEAN | NOT NULL | TRUE | Soft-disable flag |
| created_at | TIMESTAMPTZ | NOT NULL | now() | Creation time |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | Last update time |

### 5.3.2 SQLAlchemy Model

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=func.now(), onupdate=func.now()
    )

    # Relationships
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
```

### 5.3.3 Indexes

| Index | Columns | Purpose |
|---|---|---|
| `idx_users_email` | email | Login lookup |
| `idx_users_username` | username | Uniqueness enforcement |

### 5.3.4 Business Rules

- Email is unique and case-insensitive (lowercase before insert)
- Username is unique and case-sensitive
- Password is never stored in plain text
- `is_active = false` prevents login but preserves data
- Deleting a user cascades to their categories, expenses, and budgets
- Audit logs are not cascaded (preserved for compliance)

## 5.4 Table: categories

### 5.4.1 Definition

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| id | UUID | PRIMARY KEY | Python-generated | Category identifier |
| user_id | UUID | FK users.id, NULLABLE, INDEX | NULL | NULL for system categories |
| name | VARCHAR(100) | NOT NULL | - | Category display name |
| color | VARCHAR(7) | NOT NULL | - | HEX color (#RRGGBB) |
| icon | VARCHAR(50) | NULLABLE | NULL | Icon name for frontend |
| is_system | BOOLEAN | NOT NULL | FALSE | True for system categories |
| created_at | TIMESTAMPTZ | NOT NULL | now() | Creation time |

### 5.4.2 SQLAlchemy Model

```python
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    user = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")

    __table_args__ = (
        CheckConstraint(
            "color ~ '^#[0-9A-Fa-f]{6}$'",
            name="ck_categories_color_format"
        ),
        CheckConstraint(
            "(is_system = TRUE AND user_id IS NULL) OR "
            "(is_system = FALSE AND user_id IS NOT NULL)",
            name="ck_categories_system_consistency"
        ),
    )
```

### 5.4.3 Indexes

| Index | Columns | Purpose |
|---|---|---|
| `idx_categories_user_id` | user_id | Filter user's custom categories |
| `idx_categories_is_system` | is_system | Query system categories |

### 5.4.4 Business Rules

- System categories: `user_id IS NULL` and `is_system = TRUE`
- Custom categories: `user_id = current_user.id` and `is_system = FALSE`
- Users cannot create, update, or delete system categories
- Custom category names must be unique within a user's scope
- Color must be valid HEX format
- Categories with expenses cannot be deleted (or expenses must be reassigned)
- For MVP: categories with expenses cannot be deleted (returns 409)

### 5.4.5 Uniqueness Constraint

PostgreSQL and SQLite handle NULL differently in unique constraints:

- PostgreSQL: `UNIQUE(user_id, name)` allows multiple NULL user_id rows
- SQLite: same behavior for NULL

To enforce uniqueness within a user's categories, use a partial unique index:

```sql
CREATE UNIQUE INDEX idx_categories_user_name_unique
ON categories (user_id, name)
WHERE user_id IS NOT NULL;
```

For system categories, uniqueness is enforced by application logic during
seeding (idempotent check).

## 5.5 Table: expenses

### 5.5.1 Definition

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| id | UUID | PRIMARY KEY | Python-generated | Expense identifier |
| user_id | UUID | FK users.id, NOT NULL, INDEX | - | Owner |
| category_id | UUID | FK categories.id, NOT NULL, INDEX | - | Category |
| amount | NUMERIC(12,2) | NOT NULL, CHECK > 0 | - | Amount in USD |
| currency | VARCHAR(3) | NOT NULL | 'USD' | Currency code |
| date | DATE | NOT NULL, INDEX | - | Expense date |
| note | TEXT | NULLABLE | NULL | Optional note |
| created_at | TIMESTAMPTZ | NOT NULL | now() | Creation time |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | Last update |

### 5.5.2 SQLAlchemy Model

```python
class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    category_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD"
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
        CheckConstraint("currency = 'USD'", name="ck_expenses_currency_usd"),
    )
```

### 5.5.3 Indexes

| Index | Columns | Purpose |
|---|---|---|
| `idx_expenses_user_id` | user_id | User isolation |
| `idx_expenses_user_date` | (user_id, date DESC) | Dashboard month queries |
| `idx_expenses_user_category` | (user_id, category_id) | Category aggregation |
| `idx_expenses_category_id` | category_id | Join performance |

### 5.5.4 Business Rules

- Amount must be positive and have at most 2 decimal places
- Amount maximum is 9,999,999,999.99
- Category must belong to the same user or be a system category
- Date is stored without timezone
- Currency is fixed to USD in MVP
- Note is optional, max 500 characters (enforced at schema level)
- Deleting a category with expenses is restricted (RESTRICT)

## 5.6 Table: budgets

### 5.6.1 Definition

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| id | UUID | PRIMARY KEY | Python-generated | Budget identifier |
| user_id | UUID | FK users.id, NOT NULL | - | Owner |
| year_month | CHAR(7) | NOT NULL | - | Format: YYYY-MM |
| amount | NUMERIC(12,2) | NOT NULL, CHECK > 0 | - | Monthly budget |
| created_at | TIMESTAMPTZ | NOT NULL | now() | Creation time |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | Last update |

### 5.6.2 SQLAlchemy Model

```python
class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    year_month: Mapped[str] = mapped_column(String(7), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="budgets")

    __table_args__ = (
        UniqueConstraint("user_id", "year_month", name="uq_budgets_user_month"),
        CheckConstraint("amount > 0", name="ck_budgets_amount_positive"),
        CheckConstraint(
            "year_month ~ '^[0-9]{4}-[0-9]{2}$'",
            name="ck_budgets_year_month_format"
        ),
    )
```

### 5.6.3 Indexes

| Index | Columns | Purpose |
|---|---|---|
| `uq_budgets_user_month` | (user_id, year_month) UNIQUE | One budget per user per month |
| `idx_budgets_user_ym` | (user_id, year_month) | Query performance |

### 5.6.4 Business Rules

- One budget per user per month (enforced by unique constraint)
- Setting a budget for an existing month performs an upsert
- year_month format is strictly YYYY-MM
- Amount must be positive
- Deleting a budget does not affect expenses

## 5.7 Table: audit_logs

### 5.7.1 Definition

| Column | Type | Constraints | Default | Description |
|---|---|---|---|---|
| id | UUID | PRIMARY KEY | Python-generated | Log identifier |
| user_id | UUID | FK users.id, NOT NULL, INDEX | - | Actor |
| action | VARCHAR(10) | NOT NULL | - | CREATE/UPDATE/DELETE |
| entity_type | VARCHAR(20) | NOT NULL | - | expense/budget |
| entity_id | UUID | NOT NULL | - | Affected entity |
| old_value | JSONB | NULLABLE | NULL | State before change |
| new_value | JSONB | NULLABLE | NULL | State after change |
| ip_address | VARCHAR(45) | NULLABLE | NULL | Client IP |
| created_at | TIMESTAMPTZ | NOT NULL | now() | When it happened |

### 5.7.2 SQLAlchemy Model

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"),
        nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(10), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    old_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        CheckConstraint(
            "action IN ('CREATE', 'UPDATE', 'DELETE')",
            name="ck_audit_action"
        ),
        CheckConstraint(
            "entity_type IN ('expense', 'budget')",
            name="ck_audit_entity_type"
        ),
    )
```

**Note on JSONB**: PostgreSQL uses JSONB. SQLite uses JSON (stored as TEXT).
SQLAlchemy's `JSONB` type on PostgreSQL and `JSON` type on SQLite are
handled by using `JSON` from `sqlalchemy` with a variant, or by using
`JSONB` with a fallback. In practice, use:

```python
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

JSONType = JSON().with_variant(JSONB(), "postgresql")
```

### 5.7.3 Indexes

| Index | Columns | Purpose |
|---|---|---|
| `idx_audit_user_created` | (user_id, created_at DESC) | User audit trail |
| `idx_audit_entity` | (entity_type, entity_id) | Entity history |
| `idx_audit_action` | action | Filter by action type |

### 5.7.4 Business Rules

- Written in the same transaction as the business operation
- If audit write fails, the business operation is rolled back
- Not exposed via API
- Preserved even if the user is deleted (no cascade)
- `old_value` is NULL for CREATE
- `new_value` is NULL for DELETE
- Both are populated for UPDATE

### 5.7.5 Example Records

**CREATE**:
```json
{
  "user_id": "uuid-a",
  "action": "CREATE",
  "entity_type": "expense",
  "entity_id": "uuid-e1",
  "old_value": null,
  "new_value": {
    "amount": "125.50",
    "category_id": "uuid-c1",
    "date": "2026-10-15",
    "note": "Lunch"
  },
  "ip_address": "203.0.113.5",
  "created_at": "2026-10-15T12:34:56Z"
}
```

**UPDATE**:
```json
{
  "user_id": "uuid-a",
  "action": "UPDATE",
  "entity_type": "expense",
  "entity_id": "uuid-e1",
  "old_value": {
    "amount": "125.50",
    "category_id": "uuid-c1",
    "date": "2026-10-15",
    "note": "Lunch"
  },
  "new_value": {
    "amount": "150.00",
    "category_id": "uuid-c1",
    "date": "2026-10-15",
    "note": "Lunch with team"
  },
  "ip_address": "203.0.113.5",
  "created_at": "2026-10-15T14:22:10Z"
}
```

**DELETE**:
```json
{
  "user_id": "uuid-a",
  "action": "DELETE",
  "entity_type": "expense",
  "entity_id": "uuid-e1",
  "old_value": {
    "amount": "150.00",
    "category_id": "uuid-c1",
    "date": "2026-10-15",
    "note": "Lunch with team"
  },
  "new_value": null,
  "ip_address": "203.0.113.5",
  "created_at": "2026-10-15T18:45:33Z"
}
```

## 5.8 Indexes and Constraints Summary

### 5.8.1 All Indexes

| Table | Index Name | Columns | Type |
|---|---|---|---|
| users | idx_users_email | email | Unique |
| users | idx_users_username | username | Unique |
| categories | idx_categories_user_id | user_id | B-tree |
| categories | idx_categories_is_system | is_system | B-tree |
| categories | idx_categories_user_name_unique | (user_id, name) WHERE user_id IS NOT NULL | Partial unique |
| expenses | idx_expenses_user_id | user_id | B-tree |
| expenses | idx_expenses_user_date | (user_id, date DESC) | B-tree |
| expenses | idx_expenses_user_category | (user_id, category_id) | B-tree |
| expenses | idx_expenses_category_id | category_id | B-tree |
| budgets | uq_budgets_user_month | (user_id, year_month) | Unique |
| budgets | idx_budgets_user_ym | (user_id, year_month) | B-tree |
| audit_logs | idx_audit_user_created | (user_id, created_at DESC) | B-tree |
| audit_logs | idx_audit_entity | (entity_type, entity_id) | B-tree |
| audit_logs | idx_audit_action | action | B-tree |

### 5.8.2 All Check Constraints

| Table | Constraint | Expression |
|---|---|---|
| categories | ck_categories_color_format | color matches ^#[0-9A-Fa-f]{6}$ |
| categories | ck_categories_system_consistency | (is_system AND user_id IS NULL) OR (NOT is_system AND user_id IS NOT NULL) |
| expenses | ck_expenses_amount_positive | amount > 0 |
| expenses | ck_expenses_currency_usd | currency = 'USD' |
| budgets | ck_budgets_amount_positive | amount > 0 |
| budgets | ck_budgets_year_month_format | year_month matches ^[0-9]{4}-[0-9]{2}$ |
| audit_logs | ck_audit_action | action IN ('CREATE','UPDATE','DELETE') |
| audit_logs | ck_audit_entity_type | entity_type IN ('expense','budget') |

### 5.8.3 All Foreign Keys

| Table | Column | References | On Delete |
|---|---|---|---|
| categories | user_id | users.id | CASCADE |
| expenses | user_id | users.id | CASCADE |
| expenses | category_id | categories.id | RESTRICT |
| budgets | user_id | users.id | CASCADE |
| audit_logs | user_id | users.id | (no cascade) |

**SQLite note**: Foreign keys are enforced only when `PRAGMA foreign_keys = ON`
is set per connection. This is configured in the SQLAlchemy engine event.

## 5.9 Seed Data

### 5.9.1 System Categories

Ten categories are seeded. They are idempotent: re-running the seed does
not create duplicates.

| Name | Color | Icon |
|---|---|---|
| Food & Dining | #EF4444 | utensils |
| Groceries | #F97316 | shopping-cart |
| Transportation | #EAB308 | car |
| Housing & Rent | #22C55E | home |
| Utilities | #14B8A6 | zap |
| Entertainment | #3B82F6 | film |
| Shopping | #8B5CF6 | bag |
| Health & Fitness | #EC4899 | heart |
| Travel | #06B6D4 | plane |
| Other | #6B7280 | more-horizontal |

### 5.9.2 Seed Implementation

```python
SYSTEM_CATEGORIES = [
    {"name": "Food & Dining", "color": "#EF4444", "icon": "utensils"},
    {"name": "Groceries", "color": "#F97316", "icon": "shopping-cart"},
    {"name": "Transportation", "color": "#EAB308", "icon": "car"},
    {"name": "Housing & Rent", "color": "#22C55E", "icon": "home"},
    {"name": "Utilities", "color": "#14B8A6", "icon": "zap"},
    {"name": "Entertainment", "color": "#3B82F6", "icon": "film"},
    {"name": "Shopping", "color": "#8B5CF6", "icon": "bag"},
    {"name": "Health & Fitness", "color": "#EC4899", "icon": "heart"},
    {"name": "Travel", "color": "#06B6D4", "icon": "plane"},
    {"name": "Other", "color": "#6B7280", "icon": "more-horizontal"},
]


def seed_categories(session: Session) -> None:
    for cat in SYSTEM_CATEGORIES:
        exists = session.query(Category).filter(
            Category.name == cat["name"],
            Category.is_system.is_(True),
        ).first()
        if not exists:
            session.add(Category(
                user_id=None,
                name=cat["name"],
                color=cat["color"],
                icon=cat["icon"],
                is_system=True,
            ))
    session.commit()
```

### 5.9.3 When Seeding Runs

| Environment | Trigger |
|---|---|
| PostgreSQL production | Alembic migration `002_seed_categories` |
| SQLite fallback | After `Base.metadata.create_all()` |
| SQLite tests | After `Base.metadata.create_all()` |
| Docker Compose | Alembic migration on startup |

## 5.10 Migration Strategy

### 5.10.1 Alembic Setup

```
backend/alembic/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    └── 002_seed_categories.py
backend/alembic.ini
```

### 5.10.2 Migration Files

**001_initial_schema.py**:
- Creates users, categories, expenses, budgets, audit_logs
- Adds all indexes and constraints

**002_seed_categories.py**:
- Inserts 10 system categories
- Idempotent (checks existence before insert)
- Downgrade removes system categories

### 5.10.3 Migration Execution

| Environment | Command | When |
|---|---|---|
| Local PostgreSQL | `uv run alembic upgrade head` | Developer runs manually |
| Docker Compose | Automatic on container start | Entrypoint script |
| Render production | `alembic upgrade head` in deploy step | CI/CD |
| SQLite fallback | `Base.metadata.create_all()` | On startup, no Alembic |
| SQLite tests | `Base.metadata.create_all()` | In test fixture |

### 5.10.4 Why Fallback Does Not Use Alembic

- Fallback data is temporary
- Migration history is unnecessary for a fresh SQLite file
- `create_all()` is faster and simpler
- Avoids Alembic compatibility issues with SQLite

### 5.10.5 Alembic Configuration

```python
# alembic/env.py
from app.models.base import Base
from app.models import user, category, expense, budget, audit_log
from app.config import settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

## 5.11 Amount Precision Rules

### 5.11.1 Why Decimal

Floating-point numbers cannot represent decimal fractions exactly:

```python
>>> 0.1 + 0.2
0.30000000000000004
```

For money, this is unacceptable. All amounts use `Decimal`.

### 5.11.2 Rules by Layer

| Layer | Type | Example |
|---|---|---|
| Database (PostgreSQL) | NUMERIC(12,2) | 125.50 |
| Database (SQLite) | NUMERIC (stored as REAL) | 125.5 |
| Python | Decimal | Decimal("125.50") |
| Pydantic | condecimal(max_digits=12, decimal_places=2) | Decimal("125.50") |
| JSON request/response | String | "125.50" |
| Frontend input | String | "125.50" |
| Frontend display | Formatted string | "$125.50" |
| Audit log | String | "125.50" |

### 5.11.3 SQLite Decimal Handling

SQLite does not have a native DECIMAL type. SQLAlchemy stores `Numeric`
as `REAL` on SQLite, which is a floating-point type. To avoid precision
loss:

- Read values back as `Decimal` using SQLAlchemy's type coercion
- Always quantize to 2 decimal places before comparison
- Use `Decimal.quantize(Decimal("0.01"))` in aggregation code

```python
def to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    return Decimal(str(value)).quantize(Decimal("0.01"))
```

### 5.11.4 Aggregation Rules

- Sum in the database using `func.sum(Expense.amount)`
- Result is cast to Decimal in Python
- Quantize to 2 decimal places before returning
- Compare using Decimal, never float

```python
total = db.query(func.sum(Expense.amount)).filter(...).scalar()
total = to_decimal(total or Decimal("0"))
```

## 5.12 Date and Timezone Rules

### 5.12.1 Rules

| Data | Type | Timezone | Rationale |
|---|---|---|---|
| Expense date | DATE | None | A day is a day, regardless of timezone |
| created_at | TIMESTAMPTZ | UTC | Audit trail requires absolute time |
| updated_at | TIMESTAMPTZ | UTC | Same |
| year_month | CHAR(7) | None | String representation of a month |

### 5.12.2 Why DATE for Expense Date

If expense date were TIMESTAMPTZ:

- An expense entered at 23:00 on Oct 31 in UTC+8 would be Oct 31 15:00 UTC
- A query for October might include or exclude it depending on interpretation
- Month boundaries become ambiguous

Using DATE eliminates this entirely. The user picks a date. That date is
stored. That date belongs to that month.

### 5.12.3 Month Range Query

```python
from datetime import date

def month_range(year_month: str) -> tuple[date, date]:
    year, month = map(int, year_month.split("-"))
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end

# Usage
start, end = month_range("2026-10")
query = query.filter(Expense.date >= start, Expense.date < end)
```

### 5.12.4 Default Date

- Frontend defaults the date input to today
- "Today" is determined by the browser's local timezone
- Backend stores whatever date it receives
- Backend does not re-interpret or shift the date

### 5.12.5 Timestamp Defaults

- `created_at` and `updated_at` use `func.now()` (database time)
- PostgreSQL `now()` returns transaction start time in UTC
- SQLite `CURRENT_TIMESTAMP` returns UTC
- Both are consistent for audit purposes

## 5.13 Database Initialization Flow

### 5.13.1 Startup Sequence

```
1. Load settings from environment
2. Determine DATABASE_URL
3. If DATABASE_URL starts with "sqlite":
     a. Create engine with check_same_thread=False
     b. Base.metadata.create_all(engine)
     c. seed_categories(session)
     d. is_fallback = False (SQLite is intentional, not fallback)
4. Else (PostgreSQL):
     a. Try to create engine with connect_timeout=5
     b. Try to connect and run SELECT 1
     c. If success:
          - is_fallback = False
          - Alembic migrations already applied in deploy step
     d. If failure:
          - Log WARNING
          - Create SQLite engine
          - Base.metadata.create_all(engine)
          - seed_categories(session)
          - is_fallback = True
5. Store is_fallback in app state for health check
```

### 5.13.2 Health Check Reporting

```python
@router.get("/health")
def health(request: Request):
    is_fallback = request.app.state.is_fallback
    db_type = "sqlite" if is_fallback else "postgresql"
    return {
        "status": "degraded" if is_fallback else "ok",
        "database": db_type,
        "fallback_active": is_fallback,
        "version": settings.APP_VERSION,
    }
```

### 5.13.3 SQLite Engine Configuration

```python
engine = create_engine(
    "sqlite:///./fallback.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # For in-memory tests
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

### 5.13.4 PostgreSQL Engine Configuration

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 5},
)
```

## 5.14 Data Volume Assumptions

| Entity | Expected Volume |
|---|---|
| Users | < 100 (demo and peer review) |
| Categories per user | 10 system + < 20 custom |
| Expenses per user per month | < 200 |
| Expenses per user total | < 2000 |
| Budgets per user | 1 per month |
| Audit logs per user | ~3x expense count |

These volumes are well within SQLite and Render free PostgreSQL limits.

## 5.15 Backup and Recovery

### 5.15.1 MVP Scope

- No automated backups
- PostgreSQL data is lost when Render free database expires (30 days)
- SQLite fallback data is lost on container restart
- This is documented in `ops/runbook.md`

### 5.15.2 Manual Export

For demonstration purposes, a manual export command is documented:

```bash
# PostgreSQL
pg_dump $DATABASE_URL > backup.sql

# SQLite
sqlite3 fallback.db .dump > backup.sql
```

### 5.15.3 Future Improvements

Listed in `ops/runbook.md` as out of scope:
- Automated daily backups
- Point-in-time recovery
- Cross-region replication
- Backup restoration testing

## 5.16 Database Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Primary key type | UUID | No collision across environments, safe for distributed generation |
| UUID generation | Python-side | Consistent across PostgreSQL and SQLite |
| Amount type | NUMERIC(12,2) | Exact decimal representation |
| Date type | DATE | Avoids timezone ambiguity for month attribution |
| Budget key | (user_id, year_month) | One budget per user per month |
| year_month type | CHAR(7) | Simple, sortable, queryable |
| Audit entity_id | UUID without FK | Supports multiple entity types, survives deletion |
| Audit JSON | JSONB (PG) / JSON (SQLite) | Flexible schema for old/new values |
| Category deletion | RESTRICT when used | Prevents orphaned expenses |
| User deletion | CASCADE | Removes all user data |
| System categories | user_id NULL | Distinguishes from user-created |
| Color storage | HEX string | Direct use in frontend |
| Currency | Fixed USD | MVP scope |
| Indexes | Query-driven | Based on actual access patterns |
| Fallback | SQLite on startup only | Simplicity; no runtime switching |
```

---