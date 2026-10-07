# Chapter 6: Backend Design

## 6.1 Directory Structure and Layering

### 6.1.1 Full Backend Tree

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── expense.py
│   │   ├── budget.py
│   │   └── audit_log.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── expense.py
│   │   ├── budget.py
│   │   └── dashboard.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── expenses.py
│   │   ├── budgets.py
│   │   ├── dashboard.py
│   │   └── health.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── category_service.py
│   │   ├── expense_service.py
│   │   ├── budget_service.py
│   │   └── dashboard_service.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py
│   │   ├── password.py
│   │   └── dependencies.py
│   ├── audit/
│   │   ├── __init__.py
│   │   └── logger.py
│   └── core/
│       ├── __init__.py
│       ├── errors.py
│       └── logging.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_password.py
│   │   ├── test_jwt.py
│   │   ├── test_expense_service.py
│   │   ├── test_budget_service.py
│   │   ├── test_category_service.py
│   │   ├── test_dashboard_service.py
│   │   └── test_audit.py
│   └── integration/
│       ├── test_auth_api.py
│       ├── test_categories_api.py
│       ├── test_expenses_api.py
│       ├── test_budgets_api.py
│       ├── test_dashboard_api.py
│       ├── test_isolation.py
│       └── test_health_api.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       └── 002_seed_categories.py
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

### 6.1.2 Layer Responsibilities

| Layer | Directory | Responsibility | Must Not |
|---|---|---|---|
| Entry | `main.py` | App factory, middleware, startup, router mounting | Contain business logic |
| Config | `config.py` | Load settings from environment | Import from app modules |
| Database | `database.py` | Engine creation, session factory, fallback | Contain queries |
| Routers | `routers/` | Parse request, call service, shape response | Contain business logic |
| Services | `services/` | Business rules, transactions, audit | Know about HTTP |
| Models | `models/` | ORM definitions, relationships | Contain business logic |
| Schemas | `schemas/` | Request/response validation | Contain database access |
| Auth | `auth/` | JWT, password, dependencies | Contain business logic |
| Audit | `audit/` | Write audit log entries | Contain business logic |
| Core | `core/` | Errors, logging, utilities | Import routers or services |

### 6.1.3 Dependency Direction

```
main.py
  → routers
      → services
          → models
          → auth (for current_user)
          → audit
          → core (errors)
  → database
  → config
```

Dependencies point inward. Models never import services. Services never
import routers.

## 6.2 Configuration Management

### 6.2.1 Settings Class

```python
# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"
    DB_CONNECT_TIMEOUT: int = 5

    # JWT
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_ISSUER: str = "expense-tracker"
    JWT_AUDIENCE: str = "expense-tracker-api"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # App
    ENVIRONMENT: str = "development"
    APP_VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 6.2.2 Settings Usage

| Module | Uses |
|---|---|
| `database.py` | DATABASE_URL, DB_CONNECT_TIMEOUT |
| `auth/jwt.py` | JWT_SECRET, JWT_ALGORITHM, expiry, issuer, audience |
| `auth/password.py` | (no settings needed) |
| `main.py` | CORS_ORIGINS, APP_VERSION, LOG_LEVEL |
| `routers/health.py` | APP_VERSION |

### 6.2.3 Environment Validation

On startup, the app validates:

- `JWT_SECRET` is not the default value in production
- `DATABASE_URL` is a valid URL
- `CORS_ORIGINS` is a list

If validation fails, the app refuses to start with a clear error message.

```python
def validate_settings(settings: Settings) -> None:
    if settings.ENVIRONMENT == "production":
        if settings.JWT_SECRET == "dev-secret-change-in-production":
            raise RuntimeError("JWT_SECRET must be set in production")
        if settings.JWT_SECRET == "":
            raise RuntimeError("JWT_SECRET cannot be empty")
```

## 6.3 JWT Authentication

### 6.3.1 Token Creation

```python
# app/auth/jwt.py
from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt

from app.config import get_settings

settings = get_settings()


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
```

### 6.3.2 Token Validation

```python
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],  # fixed, never from token
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except jwt.ExpiredSignatureError:
        raise AppError("TOKEN_EXPIRED", "Token has expired", 401)
    except jwt.JWTClaimsError:
        raise AppError("TOKEN_INVALID", "Invalid token claims", 401)
    except jwt.JWTError:
        raise AppError("TOKEN_INVALID", "Invalid token", 401)

    if payload.get("type") != "access":
        raise AppError("TOKEN_INVALID", "Invalid token type", 401)

    return payload
```

### 6.3.3 Security Rules

| Rule | Implementation |
|---|---|
| Algorithm fixed | `algorithms=[settings.JWT_ALGORITHM]`, never from token header |
| Reject alg=none | python-jose rejects automatically when algorithms is fixed |
| Validate exp | `jwt.decode` checks exp by default |
| Validate aud | `audience=` parameter |
| Validate iss | `issuer=` parameter |
| Validate type | Check `payload["type"] == "access"` |
| Secret from env | `settings.JWT_SECRET` |
| Secret length | >= 32 characters recommended |

### 6.3.4 Token Structure

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "iss": "expense-tracker",
  "aud": "expense-tracker-api",
  "iat": 1728998200,
  "exp": 1729084600,
  "type": "access"
}
```

### 6.3.5 Why No Refresh Token

- MVP scope
- 24-hour access token is acceptable for demo
- Reduces complexity: no refresh endpoint, no token rotation, no family tracking
- Documented as a known limitation
- If added later: refresh token in HttpOnly cookie, rotation, family revocation

## 6.4 Password Hashing

### 6.4.1 Implementation

```python
# app/auth/password.py
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### 6.4.2 Rules

| Rule | Value |
|---|---|
| Algorithm | bcrypt |
| Rounds | 12 (default, secure) |
| Salt | Automatic, unique per password |
| Max password length | 72 bytes (bcrypt limit) |
| Min password length | 8 characters (validated at schema level) |
| Storage | `hashed_password` column, never plain |

### 6.4.3 Password Validation

Validation happens at the Pydantic schema level, not in the password module:

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=72)
```

### 6.4.4 Timing Attack Mitigation

`verify_password` always runs bcrypt even if the user does not exist. This
prevents timing attacks that could reveal whether an email is registered.

```python
def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower()).first()

    if user is None:
        # Run a dummy hash to equalize timing
        verify_password(password, DUMMY_HASH)
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
```

## 6.5 Dependency Injection

### 6.5.1 Database Session

```python
# app/database.py
from sqlalchemy.orm import sessionmaker, Session

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 6.5.2 Current User

```python
# app/auth/dependencies.py
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError("UNAUTHORIZED", "Missing authentication", 401)

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")

    if not user_id:
        raise AppError("TOKEN_INVALID", "Missing subject", 401)

    user = db.get(User, UUID(user_id))

    if user is None:
        raise AppError("TOKEN_INVALID", "User not found", 401)

    if not user.is_active:
        raise AppError("USER_INACTIVE", "User account is disabled", 401)

    return user
```

### 6.5.3 Settings

```python
def get_settings_dep() -> Settings:
    return get_settings()
```

### 6.5.4 Client IP

```python
def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
```

### 6.5.5 Dependency Graph

```
Request
  │
  ├── get_db → Session
  │
  ├── get_current_user
  │     ├── HTTPBearer → credentials
  │     ├── get_db → Session
  │     └── decode_access_token
  │
  └── get_client_ip
        └── Request
```

## 6.6 Auth Service

### 6.6.1 Register

```python
# app/services/auth_service.py
def register_user(
    db: Session,
    email: str,
    username: str,
    password: str,
) -> User:
    email = email.lower().strip()
    username = username.strip()

    if db.query(User).filter(User.email == email).first():
        raise AppError("DUPLICATE_EMAIL", "Email already registered", 409, "email")

    if db.query(User).filter(User.username == username).first():
        raise AppError("DUPLICATE_USERNAME", "Username already taken", 409, "username")

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### 6.6.2 Login

```python
def login_user(db: Session, email: str, password: str) -> tuple[User, str]:
    user = authenticate_user(db, email.lower().strip(), password)

    if user is None:
        logger.warning("auth.login_failed", email_hash=hash_email(email))
        raise AppError("INVALID_CREDENTIALS", "Invalid email or password", 401)

    if not user.is_active:
        raise AppError("USER_INACTIVE", "User account is disabled", 401)

    token = create_access_token(user.id)
    logger.info("auth.login", user_id=str(user.id))
    return user, token
```

### 6.6.3 Get Current User

```python
def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise AppError("NOT_FOUND", "User not found", 404)
    return user
```

## 6.7 Category Service

### 6.7.1 List Categories

```python
def list_categories(db: Session, user: User) -> list[Category]:
    return (
        db.query(Category)
        .filter(
            or_(
                Category.user_id.is_(None),  # system
                Category.user_id == user.id,  # custom
            )
        )
        .order_by(Category.is_system.desc(), Category.name)
        .all()
    )
```

### 6.7.2 Create Category

```python
def create_category(
    db: Session,
    user: User,
    name: str,
    color: str,
    icon: str | None = None,
) -> Category:
    name = name.strip()

    existing = (
        db.query(Category)
        .filter(
            Category.user_id == user.id,
            func.lower(Category.name) == name.lower(),
        )
        .first()
    )
    if existing:
        raise AppError("DUPLICATE_CATEGORY", "Category already exists", 409, "name")

    category = Category(
        user_id=user.id,
        name=name,
        color=color,
        icon=icon,
        is_system=False,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
```

### 6.7.3 Delete Category

```python
def delete_category(db: Session, user: User, category_id: UUID) -> None:
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.user_id == user.id,  # must be own category
            Category.is_system.is_(False),
        )
        .first()
    )

    if category is None:
        raise AppError("NOT_FOUND", "Category not found", 404)

    expense_count = (
        db.query(func.count(Expense.id))
        .filter(Expense.category_id == category_id)
        .scalar()
    )
    if expense_count > 0:
        raise AppError(
            "CATEGORY_IN_USE",
            "Cannot delete category with existing expenses",
            409,
        )

    db.delete(category)
    db.commit()
```

### 6.7.4 Validate Category Ownership

```python
def validate_category_access(db: Session, user: User, category_id: UUID) -> Category:
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            or_(
                Category.user_id.is_(None),
                Category.user_id == user.id,
            ),
        )
        .first()
    )
    if category is None:
        # Return 404, not 403, to avoid revealing existence
        raise AppError("CATEGORY_NOT_FOUND", "Category not found", 404)
    return category
```

## 6.8 Expense Service

### 6.8.1 Create Expense

```python
def create_expense(
    db: Session,
    user: User,
    amount: Decimal,
    category_id: UUID,
    date: date,
    note: str | None,
    ip_address: str | None,
) -> Expense:
    validate_category_access(db, user, category_id)

    expense = Expense(
        user_id=user.id,
        category_id=category_id,
        amount=amount,
        currency="USD",
        date=date,
        note=note,
    )
    db.add(expense)
    db.flush()  # get id without committing

    write_audit_log(
        db=db,
        user_id=user.id,
        action="CREATE",
        entity_type="expense",
        entity_id=expense.id,
        old_value=None,
        new_value=expense_to_dict(expense),
        ip_address=ip_address,
    )

    db.commit()
    db.refresh(expense)
    logger.info(
        "expense.created",
        user_id=str(user.id),
        expense_id=str(expense.id),
        amount=str(amount),
    )
    return expense
```

### 6.8.2 List Expenses

```python
def list_expenses(
    db: Session,
    user: User,
    year_month: str | None,
    category_id: UUID | None,
    page: int,
    page_size: int,
) -> tuple[list[Expense], int]:
    query = db.query(Expense).filter(Expense.user_id == user.id)

    if year_month:
        start, end = month_range(year_month)
        query = query.filter(Expense.date >= start, Expense.date < end)

    if category_id:
        query = query.filter(Expense.category_id == category_id)

    total = query.count()

    items = (
        query
        .order_by(Expense.date.desc(), Expense.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total
```

### 6.8.3 Get Expense

```python
def get_expense(db: Session, user: User, expense_id: UUID) -> Expense:
    expense = (
        db.query(Expense)
        .filter(
            Expense.id == expense_id,
            Expense.user_id == user.id,
        )
        .first()
    )
    if expense is None:
        raise AppError("NOT_FOUND", "Expense not found", 404)
    return expense
```

### 6.8.4 Update Expense

```python
def update_expense(
    db: Session,
    user: User,
    expense_id: UUID,
    updates: dict,
    ip_address: str | None,
) -> Expense:
    expense = get_expense(db, user, expense_id)
    old_value = expense_to_dict(expense)

    if "category_id" in updates:
        validate_category_access(db, user, updates["category_id"])

    for key, value in updates.items():
        setattr(expense, key, value)

    db.flush()

    write_audit_log(
        db=db,
        user_id=user.id,
        action="UPDATE",
        entity_type="expense",
        entity_id=expense.id,
        old_value=old_value,
        new_value=expense_to_dict(expense),
        ip_address=ip_address,
    )

    db.commit()
    db.refresh(expense)
    logger.info(
        "expense.updated",
        user_id=str(user.id),
        expense_id=str(expense.id),
    )
    return expense
```

### 6.8.5 Delete Expense

```python
def delete_expense(
    db: Session,
    user: User,
    expense_id: UUID,
    ip_address: str | None,
) -> None:
    expense = get_expense(db, user, expense_id)
    old_value = expense_to_dict(expense)

    db.delete(expense)

    write_audit_log(
        db=db,
        user_id=user.id,
        action="DELETE",
        entity_type="expense",
        entity_id=expense_id,
        old_value=old_value,
        new_value=None,
        ip_address=ip_address,
    )

    db.commit()
    logger.info(
        "expense.deleted",
        user_id=str(user.id),
        expense_id=str(expense_id),
    )
```

### 6.8.6 Serialization Helper

```python
def expense_to_dict(expense: Expense) -> dict:
    return {
        "amount": str(expense.amount),
        "category_id": str(expense.category_id),
        "date": expense.date.isoformat(),
        "note": expense.note,
    }
```

## 6.9 Budget Service

### 6.9.1 Set Budget (Upsert)

```python
def set_budget(
    db: Session,
    user: User,
    year_month: str,
    amount: Decimal,
    ip_address: str | None,
) -> Budget:
    validate_year_month(year_month)

    existing = (
        db.query(Budget)
        .filter(
            Budget.user_id == user.id,
            Budget.year_month == year_month,
        )
        .first()
    )

    if existing:
        old_value = budget_to_dict(existing)
        existing.amount = amount
        db.flush()

        write_audit_log(
            db=db,
            user_id=user.id,
            action="UPDATE",
            entity_type="budget",
            entity_id=existing.id,
            old_value=old_value,
            new_value=budget_to_dict(existing),
            ip_address=ip_address,
        )

        db.commit()
        db.refresh(existing)
        logger.info("budget.updated", user_id=str(user.id), year_month=year_month)
        return existing

    budget = Budget(
        user_id=user.id,
        year_month=year_month,
        amount=amount,
    )
    db.add(budget)
    db.flush()

    write_audit_log(
        db=db,
        user_id=user.id,
        action="CREATE",
        entity_type="budget",
        entity_id=budget.id,
        old_value=None,
        new_value=budget_to_dict(budget),
        ip_address=ip_address,
    )

    db.commit()
    db.refresh(budget)
    logger.info("budget.created", user_id=str(user.id), year_month=year_month)
    return budget
```

### 6.9.2 Get Budget

```python
def get_budget(db: Session, user: User, year_month: str) -> Budget | None:
    validate_year_month(year_month)
    return (
        db.query(Budget)
        .filter(
            Budget.user_id == user.id,
            Budget.year_month == year_month,
        )
        .first()
    )
```

### 6.9.3 Delete Budget

```python
def delete_budget(
    db: Session,
    user: User,
    year_month: str,
    ip_address: str | None,
) -> None:
    budget = get_budget(db, user, year_month)
    if budget is None:
        raise AppError("NOT_FOUND", "Budget not found", 404)

    old_value = budget_to_dict(budget)
    db.delete(budget)

    write_audit_log(
        db=db,
        user_id=user.id,
        action="DELETE",
        entity_type="budget",
        entity_id=budget.id,
        old_value=old_value,
        new_value=None,
        ip_address=ip_address,
    )

    db.commit()
    logger.info("budget.deleted", user_id=str(user.id), year_month=year_month)
```

### 6.9.4 Helpers

```python
def budget_to_dict(budget: Budget) -> dict:
    return {
        "year_month": budget.year_month,
        "amount": str(budget.amount),
    }


def validate_year_month(year_month: str) -> None:
    import re
    if not re.match(r"^\d{4}-\d{2}$", year_month):
        raise AppError("INVALID_MONTH", "Invalid year_month format", 422, "year_month")
    year, month = map(int, year_month.split("-"))
    if month < 1 or month > 12:
        raise AppError("INVALID_MONTH", "Month must be 01-12", 422, "year_month")
```

## 6.10 Dashboard Service

### 6.10.1 Summary

```python
def get_summary(db: Session, user: User, year_month: str) -> dict:
    start, end = month_range(year_month)

    total_spent = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.user_id == user.id,
            Expense.date >= start,
            Expense.date < end,
        )
        .scalar()
    )
    total_spent = to_decimal(total_spent)

    transaction_count = (
        db.query(func.count(Expense.id))
        .filter(
            Expense.user_id == user.id,
            Expense.date >= start,
            Expense.date < end,
        )
        .scalar()
    )

    budget = get_budget(db, user, year_month)
    budget_amount = to_decimal(budget.amount) if budget else Decimal("0.00")

    remaining = budget_amount - total_spent
    percentage = (
        float(total_spent / budget_amount * 100)
        if budget_amount > 0
        else None
    )

    return {
        "year_month": year_month,
        "total_spent": str(total_spent),
        "budget": str(budget_amount),
        "remaining": str(remaining),
        "percentage": percentage,
        "transaction_count": transaction_count,
        "is_over_budget": total_spent > budget_amount and budget_amount > 0,
    }
```

### 6.10.2 By Category

```python
def get_by_category(db: Session, user: User, year_month: str) -> dict:
    start, end = month_range(year_month)

    rows = (
        db.query(
            Category.id,
            Category.name,
            Category.color,
            func.sum(Expense.amount).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user.id,
            Expense.date >= start,
            Expense.date < end,
        )
        .group_by(Category.id, Category.name, Category.color)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    grand_total = sum(to_decimal(r.total) for r in rows) or Decimal("0.00")

    categories = []
    for r in rows:
        amount = to_decimal(r.total)
        percentage = (
            float(amount / grand_total * 100) if grand_total > 0 else 0.0
        )
        categories.append({
            "category_id": str(r.id),
            "name": r.name,
            "color": r.color,
            "amount": str(amount),
            "percentage": round(percentage, 1),
        })

    return {
        "year_month": year_month,
        "total": str(grand_total),
        "categories": categories,
    }
```

### 6.10.3 Trend

```python
def get_trend(db: Session, user: User, months: int) -> dict:
    today = date.today()
    start_month = subtract_months(today.replace(day=1), months - 1)

    rows = (
        db.query(Expense.date, Expense.amount)
        .filter(
            Expense.user_id == user.id,
            Expense.date >= start_month,
        )
        .all()
    )

    # Aggregate in Python to avoid database-specific date functions
    buckets: dict[str, Decimal] = {}
    for d, amount in rows:
        key = d.strftime("%Y-%m")
        buckets[key] = buckets.get(key, Decimal("0.00")) + to_decimal(amount)

    result = []
    current = start_month
    for _ in range(months):
        key = current.strftime("%Y-%m")
        result.append({
            "year_month": key,
            "total": str(buckets.get(key, Decimal("0.00"))),
        })
        current = add_month(current)

    return {"months": result}
```

### 6.10.4 Cumulative

```python
def get_cumulative(db: Session, user: User, year_month: str) -> dict:
    start, end = month_range(year_month)

    rows = (
        db.query(Expense.date, func.sum(Expense.amount))
        .filter(
            Expense.user_id == user.id,
            Expense.date >= start,
            Expense.date < end,
        )
        .group_by(Expense.date)
        .all()
    )

    daily_map = {d: to_decimal(total) for d, total in rows}

    budget = get_budget(db, user, year_month)
    budget_amount = to_decimal(budget.amount) if budget else Decimal("0.00")

    days = []
    cumulative = Decimal("0.00")
    current = start
    while current < end:
        daily = daily_map.get(current, Decimal("0.00"))
        cumulative += daily
        days.append({
            "date": current.isoformat(),
            "daily": str(daily),
            "cumulative": str(cumulative),
        })
        current += timedelta(days=1)

    return {
        "year_month": year_month,
        "budget": str(budget_amount),
        "days": days,
    }
```

### 6.10.5 Heatmap

```python
def get_heatmap(db: Session, user: User, weeks: int) -> dict:
    today = date.today()
    # Align to Monday
    end = today + timedelta(days=(6 - today.weekday()))
    start = end - timedelta(weeks=weeks, days=-1)
    start = start - timedelta(days=start.weekday())

    rows = (
        db.query(Expense.date, func.sum(Expense.amount))
        .filter(
            Expense.user_id == user.id,
            Expense.date >= start,
            Expense.date <= end,
        )
        .group_by(Expense.date)
        .all()
    )

    daily_map = {d: to_decimal(total) for d, total in rows}
    max_amount = max(daily_map.values(), default=Decimal("0.00"))

    week_list = []
    current = start
    for _ in range(weeks):
        days = []
        for offset in range(7):
            day = current + timedelta(days=offset)
            days.append({
                "date": day.isoformat(),
                "amount": str(daily_map.get(day, Decimal("0.00"))),
            })
        week_list.append({
            "week_start": current.isoformat(),
            "days": days,
        })
        current += timedelta(days=7)

    return {
        "max_amount": str(max_amount),
        "weeks": week_list,
    }
```

### 6.10.6 Recent

```python
def get_recent(db: Session, user: User, limit: int) -> list[Expense]:
    return (
        db.query(Expense)
        .filter(Expense.user_id == user.id)
        .order_by(Expense.date.desc(), Expense.created_at.desc())
        .limit(limit)
        .all()
    )
```

### 6.10.7 Shared Helpers

```python
def month_range(year_month: str) -> tuple[date, date]:
    year, month = map(int, year_month.split("-"))
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def add_month(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def subtract_months(d: date, n: int) -> date:
    for _ in range(n):
        if d.month == 1:
            d = date(d.year - 1, 12, 1)
        else:
            d = date(d.year, d.month - 1, 1)
    return d


def to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))
    return Decimal(str(value)).quantize(Decimal("0.01"))
```

## 6.11 Audit Logging

### 6.11.1 Writer

```python
# app/audit/logger.py
def write_audit_log(
    db: Session,
    user_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID,
    old_value: dict | None,
    new_value: dict | None,
    ip_address: str | None,
) -> None:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
    db.add(log)
    # No commit here; caller commits
```

### 6.11.2 Rules

| Rule | Implementation |
|---|---|
| Same transaction | `write_audit_log` uses the same `db` session |
| Rollback on failure | If audit insert fails, caller's commit fails |
| No API access | No router exposes audit logs |
| Preserve on user delete | No cascade on `audit_logs.user_id` |
| Content | old_value and new_value are JSON-serializable dicts |
| IP address | Extracted from request via `get_client_ip` |

## 6.12 Error Handling

### 6.12.1 AppError

```python
# app/core/errors.py
class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        field: str | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field
        super().__init__(message)
```

### 6.12.2 Exception Handlers

```python
# app/main.py
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "code": exc.code,
            "field": exc.field,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first.get("loc", []) if loc != "body")
    return JSONResponse(
        status_code=422,
        content={
            "detail": first.get("msg", "Validation error"),
            "code": "VALIDATION_ERROR",
            "field": field or None,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error("db.error", error=str(exc))
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database unavailable",
            "code": "DATABASE_UNAVAILABLE",
            "field": None,
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error("unhandled.error", error=str(exc), type=type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "code": "INTERNAL_ERROR",
            "field": None,
        },
    )
```

### 6.12.3 Error Code Table

| Code | HTTP | Meaning | Field |
|---|---|---|---|
| VALIDATION_ERROR | 422 | Request body or query invalid | varies |
| INVALID_CREDENTIALS | 401 | Wrong email or password | - |
| TOKEN_EXPIRED | 401 | JWT expired | - |
| TOKEN_INVALID | 401 | JWT malformed or wrong claims | - |
| UNAUTHORIZED | 401 | Missing token | - |
| USER_INACTIVE | 401 | Account disabled | - |
| FORBIDDEN | 403 | Action not allowed | - |
| NOT_FOUND | 404 | Resource not found | - |
| CATEGORY_NOT_FOUND | 404 | Category missing or not owned | category_id |
| DUPLICATE_EMAIL | 409 | Email already registered | email |
| DUPLICATE_USERNAME | 409 | Username already taken | username |
| DUPLICATE_CATEGORY | 409 | Category name exists | name |
| DUPLICATE_BUDGET | 409 | Budget exists for month | year_month |
| CATEGORY_IN_USE | 409 | Category has expenses | category_id |
| INVALID_AMOUNT | 422 | Amount invalid | amount |
| INVALID_MONTH | 422 | year_month invalid | year_month |
| DATABASE_UNAVAILABLE | 503 | Database error | - |
| INTERNAL_ERROR | 500 | Unexpected | - |

## 6.13 Logging

### 6.13.1 Setup

```python
# app/core/logging.py
import logging
import json
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
```

### 6.13.2 Log Events

| Event | Level | Extra Fields |
|---|---|---|
| auth.register | INFO | user_id |
| auth.login | INFO | user_id |
| auth.login_failed | WARNING | email_hash |
| expense.created | INFO | user_id, expense_id, amount |
| expense.updated | INFO | user_id, expense_id |
| expense.deleted | INFO | user_id, expense_id |
| budget.created | INFO | user_id, year_month |
| budget.updated | INFO | user_id, year_month |
| budget.deleted | INFO | user_id, year_month |
| category.created | INFO | user_id, category_id |
| category.deleted | INFO | user_id, category_id |
| db.fallback_triggered | WARNING | error |
| db.connection_restored | INFO | - |
| db.error | ERROR | error |

### 6.13.3 Never Log

- Passwords (plain or hashed)
- JWT tokens
- Full request bodies
- Full response bodies
- Raw email addresses (use a hash)
- Database connection strings with credentials

## 6.14 SQLite Fallback Logic

### 6.14.1 Engine Selection

```python
# app/database.py
import logging
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

is_fallback = False


def create_db_engine():
    global is_fallback

    url = settings.DATABASE_URL

    if url.startswith("sqlite"):
        is_fallback = False
        return _create_sqlite_engine(url)

    try:
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": settings.DB_CONNECT_TIMEOUT},
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("db.connected", extra={"extra_fields": {"type": "postgresql"}})
        is_fallback = False
        return engine
    except Exception as e:
        logger.warning(
            "db.fallback_triggered",
            extra={"extra_fields": {"error": str(e)[:200]}},
        )
        is_fallback = True
        return _create_sqlite_engine("sqlite:///./fallback.db")


def _create_sqlite_engine(url: str):
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 6.14.2 Startup Initialization

```python
# app/main.py
@app.on_event("startup")
def on_startup():
    from app.database import engine, is_fallback
    from app.models.base import Base

    if is_fallback:
        Base.metadata.create_all(engine)
        with SessionLocal() as session:
            seed_categories(session)
        logger.info("db.fallback_initialized")
    else:
        logger.info("db.primary_initialized")
```

### 6.14.3 Health Check

```python
# app/routers/health.py
from fastapi import APIRouter
from app.database import is_fallback
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
def health():
    return {
        "status": "degraded" if is_fallback else "ok",
        "database": "sqlite" if is_fallback else "postgresql",
        "fallback_active": is_fallback,
        "version": settings.APP_VERSION,
    }
```

### 6.14.4 Fallback Rules

| Rule | Behavior |
|---|---|
| Trigger | PostgreSQL connection fails on startup |
| Timeout | 5 seconds |
| Fallback target | `sqlite:///./fallback.db` |
| Table creation | `Base.metadata.create_all(engine)` |
| Seeding | `seed_categories(session)` |
| Switch back | Requires restart |
| Data persistence | Lost on container restart |
| API behavior | All endpoints work normally |

## 6.15 Main Application

### 6.15.1 App Factory

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.config import get_settings
from app.core.logging import configure_logging
from app.core.errors import AppError
from app.routers import auth, categories, expenses, budgets, dashboard, health

settings = get_settings()
configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="Expense Tracker & Budget Dashboard API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers (see 6.12)

# Routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(expenses.router, prefix="/api/v1/expenses", tags=["expenses"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

# Serve frontend static files in production
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        index = static_dir / "index.html"
        return FileResponse(index)
```

### 6.15.2 Router Registration Order

| Order | Router | Prefix |
|---|---|---|
| 1 | health | /api/v1 |
| 2 | auth | /api/v1/auth |
| 3 | categories | /api/v1/categories |
| 4 | expenses | /api/v1/expenses |
| 5 | budgets | /api/v1/budgets |
| 6 | dashboard | /api/v1/dashboard |
| 7 | static SPA fallback | /* |

The SPA fallback must be registered last so it does not shadow API routes.

## 6.16 Backend Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | FastAPI | Auto OpenAPI, async, Pydantic |
| ORM | SQLAlchemy 2.0 | Supports PostgreSQL and SQLite |
| Session per request | `get_db` dependency | Standard pattern, clean lifecycle |
| Service layer | Separate from routers | Testable, reusable, clear boundaries |
| Audit in same transaction | Service writes, caller commits | Atomicity |
| User isolation | Query-level filter by user_id | Defense in depth |
| 404 for cross-user | Not 403 | Does not reveal existence |
| Token storage | Bearer header | Standard, works with SPA |
| Password hashing | bcrypt rounds=12 | Secure, widely used |
| JWT algorithm | HS256, fixed | Symmetric, simple, no key management |
| Validation | Pydantic v2 | Clear errors, type-safe |
| Logging | JSON structured | Parseable, searchable |
| Fallback | Startup-only SQLite | Simple, predictable |
| Static serving | FastAPI StaticFiles | Single container |
| Error format | `{detail, code, field}` | Consistent, machine-readable |
| Decimal handling | Quantize to 0.01 everywhere | Avoids float drift |
| Date handling | DATE type, no timezone | Avoids month boundary bugs |
```

---
