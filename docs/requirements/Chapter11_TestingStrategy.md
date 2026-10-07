# Chapter 11: Testing Strategy

## 11.1 Overview

Testing is organized into four layers. Each layer has a clear purpose,
a specific tool, and a defined scope.

| Layer | Tool | Scope | Location |
|---|---|---|---|
| Backend unit | pytest | Services, auth, helpers | `backend/tests/unit/` |
| Backend integration | pytest + httpx | API endpoints, database | `backend/tests/integration/` |
| Frontend unit/component | Vitest + RTL | Utils, charts, forms, pages | `frontend/src/**/*.test.ts(x)` |
| End-to-end | Playwright | Full user flows in a browser | `e2e/tests/` |

### 11.1.1 Testing Principles

| Principle | Explanation |
|---|---|
| Test behavior, not implementation | Assert on outcomes, not internals |
| One assertion per concept | Clear failure messages |
| Independent tests | No shared mutable state |
| Deterministic | No reliance on wall clock or network |
| Fast by default | Unit tests run in seconds |
| Realistic integration | Integration tests use a real database |
| Isolated E2E | Each test uses its own user |

### 11.1.2 Coverage Policy

Coverage is reported but not enforced. The project uploads coverage to
the CI summary. The goal is visibility, not a gate.

| Layer | Target | Enforced |
|---|---|---|
| Backend unit | 80%+ | No |
| Backend integration | 70%+ | No |
| Frontend unit | 80%+ | No |
| Frontend components | 70%+ | No |
| E2E | Core flows | No |

## 11.2 Backend Unit Tests

### 11.2.1 Directory Structure

```
backend/tests/
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_password.py
│   ├── test_jwt.py
│   ├── test_auth_service.py
│   ├── test_category_service.py
│   ├── test_expense_service.py
│   ├── test_budget_service.py
│   ├── test_dashboard_service.py
│   ├── test_audit_logger.py
│   └── test_decimal_helpers.py
└── integration/
    ├── __init__.py
    ├── test_auth_api.py
    ├── test_categories_api.py
    ├── test_expenses_api.py
    ├── test_budgets_api.py
    ├── test_dashboard_api.py
    ├── test_isolation.py
    ├── test_health_api.py
    └── test_agent_hooks.py
```

### 11.2.2 Fixtures (conftest.py)

```python
import pytest
from decimal import Decimal
from datetime import date
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.user import User
from app.models.category import Category
from app.auth.password import hash_password
from app.database import seed_categories


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_categories(session)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def user_a(db_session):
    user = User(
        email="a@example.com",
        username="user_a",
        hashed_password=hash_password("password123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_b(db_session):
    user = User(
        email="b@example.com",
        username="user_b",
        hashed_password=hash_password("password123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def system_category(db_session):
    return (
        db_session.query(Category)
        .filter(Category.is_system.is_(True))
        .first()
    )
```

### 11.2.3 test_password.py

```python
from app.auth.password import hash_password, verify_password


def test_hash_password_returns_hash_not_plain():
    hashed = hash_password("password123")
    assert hashed != "password123"
    assert hashed.startswith("$2b$")


def test_verify_correct_password():
    hashed = hash_password("password123")
    assert verify_password("password123", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("password123")
    assert verify_password("wrong", hashed) is False


def test_hash_is_salted():
    h1 = hash_password("password123")
    h2 = hash_password("password123")
    assert h1 != h2
```

### 11.2.4 test_jwt.py

```python
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from jose import jwt

from app.auth.jwt import create_access_token, decode_access_token
from app.config import get_settings
from app.core.errors import AppError


def test_create_access_token_contains_claims():
    user_id = uuid4()
    token = create_access_token(user_id)
    payload = jwt.decode(
        token,
        get_settings().JWT_SECRET,
        algorithms=["HS256"],
        audience=get_settings().JWT_AUDIENCE,
        issuer=get_settings().JWT_ISSUER,
    )
    assert payload["sub"] == str(user_id)
    assert payload["iss"] == get_settings().JWT_ISSUER
    assert payload["aud"] == get_settings().JWT_AUDIENCE
    assert payload["type"] == "access"


def test_decode_valid_token():
    user_id = uuid4()
    token = create_access_token(user_id)
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)


def test_decode_expired_token_raises():
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid4()),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int((now - timedelta(hours=2)).timestamp()),
        "exp": int((now - timedelta(hours=1)).timestamp()),
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    with pytest.raises(AppError) as exc:
        decode_access_token(token)
    assert exc.value.code == "TOKEN_EXPIRED"


def test_decode_wrong_audience_raises():
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid4()),
        "iss": settings.JWT_ISSUER,
        "aud": "wrong-audience",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    with pytest.raises(AppError) as exc:
        decode_access_token(token)
    assert exc.value.code == "TOKEN_INVALID"


def test_decode_wrong_issuer_raises():
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid4()),
        "iss": "wrong-issuer",
        "aud": settings.JWT_AUDIENCE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    with pytest.raises(AppError):
        decode_access_token(token)
```

### 11.2.5 test_auth_service.py

```python
import pytest

from app.services.auth_service import register_user, login_user
from app.core.errors import AppError


def test_register_user_success(db_session):
    user = register_user(db_session, "new@example.com", "newuser", "password123")
    assert user.email == "new@example.com"
    assert user.username == "newuser"
    assert user.hashed_password != "password123"


def test_register_duplicate_email(db_session, user_a):
    with pytest.raises(AppError) as exc:
        register_user(db_session, "a@example.com", "another", "password123")
    assert exc.value.code == "DUPLICATE_EMAIL"


def test_register_duplicate_username(db_session, user_a):
    with pytest.raises(AppError) as exc:
        register_user(db_session, "other@example.com", "user_a", "password123")
    assert exc.value.code == "DUPLICATE_USERNAME"


def test_login_success_returns_token(db_session, user_a):
    user, token = login_user(db_session, "a@example.com", "password123")
    assert user.id == user_a.id
    assert isinstance(token, str)
    assert len(token) > 20


def test_login_wrong_password(db_session, user_a):
    with pytest.raises(AppError) as exc:
        login_user(db_session, "a@example.com", "wrong")
    assert exc.value.code == "INVALID_CREDENTIALS"


def test_login_nonexistent_email(db_session):
    with pytest.raises(AppError) as exc:
        login_user(db_session, "nobody@example.com", "password123")
    assert exc.value.code == "INVALID_CREDENTIALS"
```

### 11.2.6 test_expense_service.py

```python
import pytest
from decimal import Decimal
from datetime import date

from app.services.expense_service import (
    create_expense, list_expenses, get_expense,
    update_expense, delete_expense,
)
from app.core.errors import AppError


def test_create_expense(db_session, user_a, system_category):
    expense = create_expense(
        db_session, user_a,
        amount=Decimal("125.50"),
        category_id=system_category.id,
        date=date(2026, 10, 15),
        note="Lunch",
        ip_address="127.0.0.1",
    )
    assert expense.amount == Decimal("125.50")
    assert expense.user_id == user_a.id


def test_create_expense_writes_audit_log(db_session, user_a, system_category):
    from app.models.audit_log import AuditLog
    create_expense(
        db_session, user_a,
        amount=Decimal("50.00"),
        category_id=system_category.id,
        date=date(2026, 10, 15),
        note=None,
        ip_address=None,
    )
    logs = db_session.query(AuditLog).filter(
        AuditLog.user_id == user_a.id,
        AuditLog.entity_type == "expense",
    ).all()
    assert len(logs) == 1
    assert logs[0].action == "CREATE"
    assert logs[0].new_value["amount"] == "50.00"


def test_list_expenses_isolates_users(db_session, user_a, user_b, system_category):
    create_expense(db_session, user_a, Decimal("100.00"),
                   system_category.id, date(2026, 10, 1), None, None)
    create_expense(db_session, user_b, Decimal("200.00"),
                   system_category.id, date(2026, 10, 1), None, None)

    items, total = list_expenses(db_session, user_a, None, None, 1, 20)
    assert total == 1
    assert items[0].amount == Decimal("100.00")


def test_update_expense_writes_audit_log(db_session, user_a, system_category):
    from app.models.audit_log import AuditLog
    expense = create_expense(
        db_session, user_a, Decimal("50.00"),
        system_category.id, date(2026, 10, 15), None, None,
    )
    update_expense(
        db_session, user_a, expense.id,
        {"amount": Decimal("75.00")}, None,
    )
    logs = db_session.query(AuditLog).filter(
        AuditLog.entity_id == expense.id,
        AuditLog.action == "UPDATE",
    ).all()
    assert len(logs) == 1
    assert logs[0].old_value["amount"] == "50.00"
    assert logs[0].new_value["amount"] == "75.00"


def test_delete_expense_other_user_returns_404(db_session, user_a, user_b, system_category):
    expense = create_expense(
        db_session, user_a, Decimal("50.00"),
        system_category.id, date(2026, 10, 15), None, None,
    )
    with pytest.raises(AppError) as exc:
        delete_expense(db_session, user_b, expense.id, None)
    assert exc.value.status_code == 404
```

### 11.2.7 test_budget_service.py

```python
import pytest
from decimal import Decimal

from app.services.budget_service import (
    set_budget, get_budget, delete_budget,
)
from app.core.errors import AppError


def test_set_budget_creates(db_session, user_a):
    budget = set_budget(db_session, user_a, "2026-10", Decimal("2000.00"), None)
    assert budget.amount == Decimal("2000.00")
    assert budget.year_month == "2026-10"


def test_set_budget_updates_existing(db_session, user_a):
    set_budget(db_session, user_a, "2026-10", Decimal("2000.00"), None)
    updated = set_budget(db_session, user_a, "2026-10", Decimal("2500.00"), None)
    assert updated.amount == Decimal("2500.00")

    count = db_session.query(type(updated)).filter(
        type(updated).user_id == user_a.id,
        type(updated).year_month == "2026-10",
    ).count()
    assert count == 1


def test_get_budget_nonexistent_returns_none(db_session, user_a):
    assert get_budget(db_session, user_a, "2026-10") is None


def test_delete_nonexistent_returns_404(db_session, user_a):
    with pytest.raises(AppError) as exc:
        delete_budget(db_session, user_a, "2026-10", None)
    assert exc.value.status_code == 404


def test_invalid_year_month_format(db_session, user_a):
    with pytest.raises(AppError) as exc:
        set_budget(db_session, user_a, "2026-13", Decimal("1000.00"), None)
    assert exc.value.code == "INVALID_MONTH"
```

### 11.2.8 test_dashboard_service.py

```python
import pytest
from decimal import Decimal
from datetime import date

from app.services.expense_service import create_expense
from app.services.budget_service import set_budget
from app.services.dashboard_service import (
    get_summary, get_by_category, get_trend,
    get_cumulative, get_heatmap, get_recent,
)


def test_summary_with_no_expenses(db_session, user_a):
    result = get_summary(db_session, user_a, "2026-10")
    assert result["total_spent"] == "0.00"
    assert result["budget"] == "0.00"
    assert result["transaction_count"] == 0
    assert result["percentage"] is None


def test_summary_with_budget_and_expenses(db_session, user_a, system_category):
    set_budget(db_session, user_a, "2026-10", Decimal("2000.00"), None)
    create_expense(db_session, user_a, Decimal("500.00"),
                   system_category.id, date(2026, 10, 10), None, None)
    create_expense(db_session, user_a, Decimal("250.50"),
                   system_category.id, date(2026, 10, 15), None, None)

    result = get_summary(db_session, user_a, "2026-10")
    assert result["total_spent"] == "750.50"
    assert result["budget"] == "2000.00"
    assert result["remaining"] == "1249.50"
    assert result["transaction_count"] == 2
    assert result["is_over_budget"] is False


def test_summary_over_budget(db_session, user_a, system_category):
    set_budget(db_session, user_a, "2026-10", Decimal("100.00"), None)
    create_expense(db_session, user_a, Decimal("150.00"),
                   system_category.id, date(2026, 10, 10), None, None)

    result = get_summary(db_session, user_a, "2026-10")
    assert result["is_over_budget"] is True
    assert result["remaining"] == "-50.00"


def test_by_category_aggregates_correctly(db_session, user_a):
    from app.models.category import Category
    cat1 = db_session.query(Category).filter(Category.is_system.is_(True)).first()
    cat2 = db_session.query(Category).filter(Category.is_system.is_(True)).offset(1).first()

    create_expense(db_session, user_a, Decimal("100.00"),
                   cat1.id, date(2026, 10, 1), None, None)
    create_expense(db_session, user_a, Decimal("50.00"),
                   cat1.id, date(2026, 10, 2), None, None)
    create_expense(db_session, user_a, Decimal("75.00"),
                   cat2.id, date(2026, 10, 3), None, None)

    result = get_by_category(db_session, user_a, "2026-10")
    assert result["total"] == "225.00"
    assert len(result["categories"]) == 2
    assert result["categories"][0]["amount"] == "150.00"


def test_trend_includes_empty_months(db_session, user_a, system_category):
    create_expense(db_session, user_a, Decimal("100.00"),
                   system_category.id, date(2026, 8, 15), None, None)

    result = get_trend(db_session, user_a, months=3)
    assert len(result["months"]) == 3
    totals = [m["total"] for m in result["months"]]
    assert "100.00" in totals
    assert "0.00" in totals


def test_cumulative_last_day_equals_total(db_session, user_a, system_category):
    create_expense(db_session, user_a, Decimal("50.00"),
                   system_category.id, date(2026, 10, 5), None, None)
    create_expense(db_session, user_a, Decimal("75.00"),
                   system_category.id, date(2026, 10, 15), None, None)

    result = get_cumulative(db_session, user_a, "2026-10")
    last = result["days"][-1]
    assert last["cumulative"] == "125.00"


def test_heatmap_weeks_have_seven_days(db_session, user_a):
    result = get_heatmap(db_session, user_a, weeks=4)
    assert len(result["weeks"]) == 4
    for week in result["weeks"]:
        assert len(week["days"]) == 7


def test_recent_returns_limited(db_session, user_a, system_category):
    for i in range(15):
        create_expense(db_session, user_a, Decimal("10.00"),
                       system_category.id, date(2026, 10, 1 + (i % 28)),
                       None, None)

    items = get_recent(db_session, user_a, limit=5)
    assert len(items) == 5
```

### 11.2.9 test_decimal_helpers.py

```python
from decimal import Decimal
from app.services.dashboard_service import to_decimal


def test_to_decimal_from_string():
    assert to_decimal("125.50") == Decimal("125.50")


def test_to_decimal_from_float_quantizes():
    assert to_decimal(125.505) == Decimal("125.51")


def test_to_decimal_from_none():
    assert to_decimal(None) == Decimal("0.00")


def test_to_decimal_from_int():
    assert to_decimal(100) == Decimal("100.00")


def test_to_decimal_quantizes_to_two_places():
    assert to_decimal("125.555") == Decimal("125.56")
```

## 11.3 Backend Integration Tests

### 11.3.1 Test Client Fixture

```python
# backend/tests/conftest.py (additions)
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client, user_a):
    response = client.post("/api/v1/auth/login", json={
        "email": "a@example.com",
        "password": "password123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b(client, user_b):
    response = client.post("/api/v1/auth/login", json={
        "email": "b@example.com",
        "password": "password123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### 11.3.2 test_auth_api.py

```python
def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "username": "newuser",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_email(client, user_a):
    response = client.post("/api/v1/auth/register", json={
        "email": "a@example.com",
        "username": "another",
        "password": "password123",
    })
    assert response.status_code == 409
    assert response.json()["code"] == "DUPLICATE_EMAIL"


def test_register_short_password(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "username": "newuser",
        "password": "short",
    })
    assert response.status_code == 422
    assert response.json()["field"] == "password"


def test_login_success(client, user_a):
    response = client.post("/api/v1/auth/login", json={
        "email": "a@example.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, user_a):
    response = client.post("/api/v1/auth/login", json={
        "email": "a@example.com",
        "password": "wrong",
    })
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_me_with_valid_token(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "a@example.com"


def test_me_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
```

### 11.3.3 test_expenses_api.py

```python
def test_create_expense(client, auth_headers, system_category):
    response = client.post("/api/v1/expenses", json={
        "amount": "125.50",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
        "note": "Lunch",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == "125.50"
    assert data["currency"] == "USD"
    assert data["category_name"] == system_category.name


def test_create_negative_amount(client, auth_headers, system_category):
    response = client.post("/api/v1/expenses", json={
        "amount": "-10.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["field"] == "amount"


def test_create_zero_amount(client, auth_headers, system_category):
    response = client.post("/api/v1/expenses", json={
        "amount": "0",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers)
    assert response.status_code == 422


def test_create_three_decimal_places(client, auth_headers, system_category):
    response = client.post("/api/v1/expenses", json={
        "amount": "125.505",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers)
    assert response.status_code == 422


def test_create_expense_requires_auth(client, system_category):
    response = client.post("/api/v1/expenses", json={
        "amount": "10.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    })
    assert response.status_code == 401


def test_list_expenses_pagination(client, auth_headers, system_category):
    for i in range(25):
        client.post("/api/v1/expenses", json={
            "amount": "10.00",
            "category_id": str(system_category.id),
            "date": f"2026-10-{(i % 28) + 1:02d}",
        }, headers=auth_headers)

    response = client.get("/api/v1/expenses?page=1&page_size=10", headers=auth_headers)
    data = response.json()
    assert data["total"] == 25
    assert len(data["items"]) == 10
    assert data["page"] == 1


def test_list_expenses_invalid_page(client, auth_headers):
    response = client.get("/api/v1/expenses?page=0", headers=auth_headers)
    assert response.status_code == 422


def test_list_expenses_page_size_too_large(client, auth_headers):
    response = client.get("/api/v1/expenses?page_size=500", headers=auth_headers)
    assert response.status_code == 422


def test_update_expense(client, auth_headers, system_category):
    create = client.post("/api/v1/expenses", json={
        "amount": "50.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers).json()

    response = client.put(f"/api/v1/expenses/{create['id']}", json={
        "amount": "75.00",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["amount"] == "75.00"


def test_delete_expense(client, auth_headers, system_category):
    create = client.post("/api/v1/expenses", json={
        "amount": "50.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers).json()

    response = client.delete(f"/api/v1/expenses/{create['id']}", headers=auth_headers)
    assert response.status_code == 204
```

### 11.3.4 test_budgets_api.py

```python
def test_set_budget(client, auth_headers):
    response = client.put("/api/v1/budgets/2026-10", json={
        "amount": "2000.00",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["amount"] == "2000.00"


def test_get_budget_nonexistent_returns_zero(client, auth_headers):
    response = client.get("/api/v1/budgets/2026-11", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["amount"] == "0.00"


def test_invalid_year_month(client, auth_headers):
    response = client.put("/api/v1/budgets/2026-13", json={
        "amount": "2000.00",
    }, headers=auth_headers)
    assert response.status_code == 422


def test_delete_budget(client, auth_headers):
    client.put("/api/v1/budgets/2026-10", json={"amount": "2000.00"},
               headers=auth_headers)
    response = client.delete("/api/v1/budgets/2026-10", headers=auth_headers)
    assert response.status_code == 204


def test_delete_nonexistent_budget(client, auth_headers):
    response = client.delete("/api/v1/budgets/2026-11", headers=auth_headers)
    assert response.status_code == 404
```

### 11.3.5 test_dashboard_api.py

```python
def test_summary_empty_month(client, auth_headers):
    response = client.get("/api/v1/dashboard/summary?year_month=2026-10",
                          headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_spent"] == "0.00"
    assert data["transaction_count"] == 0


def test_by_category_empty(client, auth_headers):
    response = client.get("/api/v1/dashboard/by-category?year_month=2026-10",
                          headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["categories"] == []


def test_trend_default_six_months(client, auth_headers):
    response = client.get("/api/v1/dashboard/trend", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["months"]) == 6


def test_cumulative_returns_all_days(client, auth_headers):
    response = client.get("/api/v1/dashboard/cumulative?year_month=2026-10",
                          headers=auth_headers)
    assert response.status_code == 200
    days = response.json()["days"]
    assert len(days) == 31


def test_heatmap_returns_weeks(client, auth_headers):
    response = client.get("/api/v1/dashboard/heatmap?weeks=4",
                          headers=auth_headers)
    assert response.status_code == 200
    weeks = response.json()["weeks"]
    assert len(weeks) == 4


def test_recent_default_ten(client, auth_headers, system_category):
    for i in range(15):
        client.post("/api/v1/expenses", json={
            "amount": "10.00",
            "category_id": str(system_category.id),
            "date": f"2026-10-{(i % 28) + 1:02d}",
        }, headers=auth_headers)

    response = client.get("/api/v1/dashboard/recent", headers=auth_headers)
    assert len(response.json()["items"]) == 10
```

### 11.3.6 test_isolation.py

```python
def test_user_cannot_read_other_users_expense(
    client, auth_headers, auth_headers_b, system_category
):
    create = client.post("/api/v1/expenses", json={
        "amount": "50.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers).json()

    response = client.get(f"/api/v1/expenses/{create['id']}",
                          headers=auth_headers_b)
    assert response.status_code == 404


def test_user_cannot_update_other_users_expense(
    client, auth_headers, auth_headers_b, system_category
):
    create = client.post("/api/v1/expenses", json={
        "amount": "50.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers).json()

    response = client.put(f"/api/v1/expenses/{create['id']}",
                          json={"amount": "75.00"},
                          headers=auth_headers_b)
    assert response.status_code == 404


def test_user_cannot_delete_other_users_expense(
    client, auth_headers, auth_headers_b, system_category
):
    create = client.post("/api/v1/expenses", json={
        "amount": "50.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers).json()

    response = client.delete(f"/api/v1/expenses/{create['id']}",
                             headers=auth_headers_b)
    assert response.status_code == 404


def test_user_sees_only_own_expenses(
    client, auth_headers, auth_headers_b, system_category
):
    client.post("/api/v1/expenses", json={
        "amount": "100.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers)

    client.post("/api/v1/expenses", json={
        "amount": "200.00",
        "category_id": str(system_category.id),
        "date": "2026-10-15",
    }, headers=auth_headers_b)

    response = client.get("/api/v1/expenses", headers=auth_headers)
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["amount"] == "100.00"


def test_budget_isolation(client, auth_headers, auth_headers_b):
    client.put("/api/v1/budgets/2026-10", json={"amount": "2000.00"},
               headers=auth_headers)

    response = client.get("/api/v1/budgets/2026-10", headers=auth_headers_b)
    assert response.json()["amount"] == "0.00"
```

### 11.3.7 test_health_api.py

```python
def test_health_returns_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert data["database"] in ("postgresql", "sqlite")
    assert isinstance(data["fallback_active"], bool)
    assert "version" in data
```

### 11.3.8 test_agent_hooks.py

```python
import pytest
from decimal import Decimal

from agent_hooks.validate_amount import validate_amount
from agent_hooks.validate_ownership import validate_ownership


def test_validate_amount_accepts_valid():
    assert validate_amount("125.50") == Decimal("125.50")


def test_validate_amount_accepts_integer():
    assert validate_amount("100") == Decimal("100")


def test_validate_amount_rejects_negative():
    with pytest.raises(ValueError, match="positive"):
        validate_amount("-5")


def test_validate_amount_rejects_zero():
    with pytest.raises(ValueError, match="positive"):
        validate_amount("0")


def test_validate_amount_rejects_three_decimals():
    with pytest.raises(ValueError, match="2 decimal"):
        validate_amount("125.505")


def test_validate_amount_rejects_non_number():
    with pytest.raises(ValueError, match="valid number"):
        validate_amount("abc")


def test_validate_amount_rejects_over_max():
    with pytest.raises(ValueError, match="maximum"):
        validate_amount("9999999")


def test_validate_ownership_same_user():
    validate_ownership("user-a", "user-a")  # no raise


def test_validate_ownership_different_user():
    with pytest.raises(PermissionError):
        validate_ownership("user-a", "user-b")
```

## 11.4 Frontend Tests

### 11.4.1 Test Setup

```ts
// frontend/src/test/setup.ts
import "@testing-library/jest-dom";
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "./mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### 11.4.2 Utils Tests

**format.test.ts**:

```ts
import { describe, it, expect } from "vitest";
import { formatUSD, formatPercent, formatMonth } from "./format";

describe("formatUSD", () => {
  it("formats integer amounts", () => {
    expect(formatUSD("125")).toBe("$125.00");
  });
  it("formats decimal amounts", () => {
    expect(formatUSD("125.5")).toBe("$125.50");
  });
  it("formats large amounts with commas", () => {
    expect(formatUSD("1234567.89")).toBe("$1,234,567.89");
  });
  it("handles zero", () => {
    expect(formatUSD("0")).toBe("$0.00");
  });
  it("handles negative amounts", () => {
    expect(formatUSD("-50.00")).toBe("-$50.00");
  });
});

describe("formatPercent", () => {
  it("formats whole numbers", () => {
    expect(formatPercent(75)).toBe("75%");
  });
  it("formats decimals", () => {
    expect(formatPercent(62.5)).toBe("62.5%");
  });
  it("handles null", () => {
    expect(formatPercent(null)).toBe("—");
  });
});

describe("formatMonth", () => {
  it("formats year-month to readable", () => {
    expect(formatMonth("2026-10")).toBe("October 2026");
  });
});
```

**date.test.ts**:

```ts
import { describe, it, expect } from "vitest";
import { currentYearMonth, shiftMonth, monthRange } from "./date";

describe("currentYearMonth", () => {
  it("returns format YYYY-MM", () => {
    expect(currentYearMonth()).toMatch(/^\d{4}-\d{2}$/);
  });
});

describe("shiftMonth", () => {
  it("shifts forward", () => {
    expect(shiftMonth("2026-10", 1)).toBe("2026-11");
  });
  it("shifts backward", () => {
    expect(shiftMonth("2026-10", -1)).toBe("2026-09");
  });
  it("handles year boundary forward", () => {
    expect(shiftMonth("2026-12", 1)).toBe("2027-01");
  });
  it("handles year boundary backward", () => {
    expect(shiftMonth("2026-01", -1)).toBe("2025-12");
  });
});

describe("monthRange", () => {
  it("returns first and next month", () => {
    const [start, end] = monthRange("2026-10");
    expect(start.toISOString().slice(0, 10)).toBe("2026-10-01");
    expect(end.toISOString().slice(0, 10)).toBe("2026-11-01");
  });
});
```

**validation.test.ts**:

```ts
import { describe, it, expect } from "vitest";
import { amountSchema, expenseFormSchema } from "./validation";

describe("amountSchema", () => {
  it("accepts valid amount", () => {
    expect(amountSchema.safeParse("125.50").success).toBe(true);
  });
  it("accepts integer", () => {
    expect(amountSchema.safeParse("100").success).toBe(true);
  });
  it("rejects negative", () => {
    expect(amountSchema.safeParse("-5").success).toBe(false);
  });
  it("rejects zero", () => {
    expect(amountSchema.safeParse("0").success).toBe(false);
  });
  it("rejects three decimals", () => {
    expect(amountSchema.safeParse("125.505").success).toBe(false);
  });
  it("rejects non-numeric", () => {
    expect(amountSchema.safeParse("abc").success).toBe(false);
  });
});

describe("expenseFormSchema", () => {
  it("accepts valid data", () => {
    const result = expenseFormSchema.safeParse({
      amount: "125.50",
      category_id: "550e8400-e29b-41d4-a716-446655440000",
      date: "2026-10-15",
      note: "Lunch",
    });
    expect(result.success).toBe(true);
  });
  it("rejects invalid category_id", () => {
    const result = expenseFormSchema.safeParse({
      amount: "125.50",
      category_id: "not-uuid",
      date: "2026-10-15",
    });
    expect(result.success).toBe(false);
  });
  it("rejects note over 500 chars", () => {
    const result = expenseFormSchema.safeParse({
      amount: "125.50",
      category_id: "550e8400-e29b-41d4-a716-446655440000",
      date: "2026-10-15",
      note: "a".repeat(501),
    });
    expect(result.success).toBe(false);
  });
});
```

### 11.4.3 Component Tests

**BudgetProgress.test.tsx**:

```tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BudgetProgress } from "./BudgetProgress";

describe("BudgetProgress", () => {
  it("shows green when under 80%", () => {
    render(<BudgetProgress totalSpent="500" budget="1000" percentage={50} isOverBudget={false} />);
    expect(screen.getByRole("progressbar")).toHaveClass("bg-green-500");
  });

  it("shows yellow when 80-100%", () => {
    render(<BudgetProgress totalSpent="850" budget="1000" percentage={85} isOverBudget={false} />);
    expect(screen.getByRole("progressbar")).toHaveClass("bg-yellow-500");
  });

  it("shows red when over budget", () => {
    render(<BudgetProgress totalSpent="1100" budget="1000" percentage={110} isOverBudget={true} />);
    expect(screen.getByRole("progressbar")).toHaveClass("bg-red-500");
  });

  it("caps progress bar width at 100%", () => {
    render(<BudgetProgress totalSpent="2000" budget="1000" percentage={200} isOverBudget={true} />);
    expect(screen.getByRole("progressbar")).toHaveStyle({ width: "100%" });
  });

  it("shows 'No budget set' when budget is 0", () => {
    render(<BudgetProgress totalSpent="0" budget="0" percentage={null} isOverBudget={false} />);
    expect(screen.getByText("No budget set")).toBeInTheDocument();
  });

  it("displays formatted amounts", () => {
    render(<BudgetProgress totalSpent="1250.50" budget="2000.00" percentage={62.5} isOverBudget={false} />);
    expect(screen.getByText(/1,250\.50/)).toBeInTheDocument();
    expect(screen.getByText(/2,000\.00/)).toBeInTheDocument();
  });
});
```

**WeeklyHeatmap.test.tsx**:

```tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { WeeklyHeatmap } from "./WeeklyHeatmap";

const emptyWeeks = [
  {
    week_start: "2026-10-13",
    days: [
      { date: "2026-10-13", amount: "0.00" },
      { date: "2026-10-14", amount: "0.00" },
      { date: "2026-10-15", amount: "0.00" },
      { date: "2026-10-16", amount: "0.00" },
      { date: "2026-10-17", amount: "0.00" },
      { date: "2026-10-18", amount: "0.00" },
      { date: "2026-10-19", amount: "0.00" },
    ],
  },
];

describe("WeeklyHeatmap", () => {
  it("renders all days", () => {
    render(<WeeklyHeatmap weeks={emptyWeeks} maxAmount="0.00" isLoading={false} />);
    expect(screen.getAllByRole("gridcell")).toHaveLength(7);
  });

  it("uses grey for zero amount", () => {
    render(<WeeklyHeatmap weeks={emptyWeeks} maxAmount="0.00" isLoading={false} />);
    const cells = screen.getAllByRole("gridcell");
    cells.forEach((cell) => {
      expect(cell).toHaveStyle({ backgroundColor: "#F3F4F6" });
    });
  });

  it("handles maxAmount zero without crashing", () => {
    expect(() =>
      render(<WeeklyHeatmap weeks={emptyWeeks} maxAmount="0.00" isLoading={false} />)
    ).not.toThrow();
  });

  it("shows skeleton when loading", () => {
    render(<WeeklyHeatmap weeks={[]} maxAmount="0.00" isLoading={true} />);
    expect(screen.getByTestId("heatmap-skeleton")).toBeInTheDocument();
  });
});
```

**CategoryPieChart.test.tsx**:

```tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { CategoryPieChart } from "./CategoryPieChart";

describe("CategoryPieChart", () => {
  it("shows empty state when no data", () => {
    render(<CategoryPieChart data={[]} isLoading={false} />);
    expect(screen.getByText(/No expenses this month/i)).toBeInTheDocument();
  });

  it("renders with data", () => {
    const data = [
      { category_id: "1", name: "Food", color: "#EF4444", amount: "450.00", percentage: 60 },
      { category_id: "2", name: "Transport", color: "#EAB308", amount: "300.00", percentage: 40 },
    ];
    render(<CategoryPieChart data={data} isLoading={false} />);
    expect(screen.getByRole("img")).toBeInTheDocument();
  });

  it("merges to Other when more than 6 categories", () => {
    const data = Array.from({ length: 8 }, (_, i) => ({
      category_id: String(i),
      name: `Cat ${i}`,
      color: "#EF4444",
      amount: "100.00",
      percentage: 12.5,
    }));
    render(<CategoryPieChart data={data} isLoading={false} />);
    expect(screen.getByText(/Other/i)).toBeInTheDocument();
  });
});
```

**ExpenseForm.test.tsx**:

```tsx
import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ExpenseForm } from "./ExpenseForm";

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

describe("ExpenseForm", () => {
  it("shows error for empty amount", async () => {
    renderWithQuery(<ExpenseForm onSuccess={vi.fn()} onCancel={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: /save/i }));
    expect(await screen.findByText(/Invalid amount/i)).toBeInTheDocument();
  });

  it("shows error for negative amount", async () => {
    renderWithQuery(<ExpenseForm onSuccess={vi.fn()} onCancel={vi.fn()} />);
    await userEvent.type(screen.getByLabelText(/amount/i), "-50");
    await userEvent.click(screen.getByRole("button", { name: /save/i }));
    expect(await screen.findByText(/Invalid amount/i)).toBeInTheDocument();
  });

  it("shows error for three decimal places", async () => {
    renderWithQuery(<ExpenseForm onSuccess={vi.fn()} onCancel={vi.fn()} />);
    await userEvent.type(screen.getByLabelText(/amount/i), "125.505");
    await userEvent.click(screen.getByRole("button", { name: /save/i }));
    expect(await screen.findByText(/Invalid amount/i)).toBeInTheDocument();
  });

  it("calls onCancel when cancel clicked", async () => {
    const onCancel = vi.fn();
    renderWithQuery(<ExpenseForm onSuccess={vi.fn()} onCancel={onCancel} />);
    await userEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });
});
```

**LoginPage.test.tsx**:

```tsx
import { describe, it, expect } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LoginPage } from "./LoginPage";
import { AuthProvider } from "../context/AuthContext";
import { ToastProvider } from "../context/ToastContext";

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <AuthProvider>
          <ToastProvider>
            <LoginPage />
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("LoginPage", () => {
  it("renders email and password fields", () => {
    renderPage();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("shows validation error for invalid email", async () => {
    renderPage();
    await userEvent.type(screen.getByLabelText(/email/i), "not-an-email");
    await userEvent.type(screen.getByLabelText(/password/i), "password123");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
  });

  it("shows error on invalid credentials", async () => {
    renderPage();
    await userEvent.type(screen.getByLabelText(/email/i), "a@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "wrong");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    // MSW returns 401
    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });
});
```

### 11.4.4 MSW Handlers

```ts
// frontend/src/test/mocks/handlers.ts
import { http, HttpResponse } from "msw";

const API = "http://localhost:8000/api/v1";

export const handlers = [
  http.post(`${API}/auth/login`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string };
    if (body.password === "password123") {
      return HttpResponse.json({
        access_token: "test-token",
        token_type: "bearer",
        user: {
          id: "1",
          email: body.email,
          username: "testuser",
          is_active: true,
          created_at: "2026-10-15T00:00:00Z",
        },
      });
    }
    return HttpResponse.json(
      { detail: "Invalid email or password", code: "INVALID_CREDENTIALS", field: null },
      { status: 401 }
    );
  }),

  http.get(`${API}/auth/me`, () => {
    return HttpResponse.json({
      id: "1",
      email: "test@example.com",
      username: "testuser",
      is_active: true,
      created_at: "2026-10-15T00:00:00Z",
    });
  }),

  http.get(`${API}/categories`, () => {
    return HttpResponse.json({ categories: [] });
  }),

  http.get(`${API}/expenses`, () => {
    return HttpResponse.json({ items: [], total: 0, page: 1, page_size: 20 });
  }),

  http.get(`${API}/dashboard/summary`, () => {
    return HttpResponse.json({
      year_month: "2026-10",
      total_spent: "0.00",
      budget: "0.00",
      remaining: "0.00",
      percentage: null,
      transaction_count: 0,
      is_over_budget: false,
    });
  }),
];
```

## 11.5 End-to-End Tests

### 11.5.1 Playwright Setup

```
e2e/
├── tests/
│   ├── happy-path.spec.ts
│   ├── isolation.spec.ts
│   └── month-switch.spec.ts
├── fixtures/
│   ├── users.ts
│   └── helpers.ts
├── playwright.config.ts
├── package.json
└── README.md
```

**playwright.config.ts**:

```ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 60000,
  fullyParallel: false,
  retries: 1,
  workers: 1,
  reporter: [["html"], ["list"]],
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:8000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  webServer: process.env.CI
    ? undefined
    : {
        command: "docker compose up --build",
        url: "http://localhost:8000/api/v1/health",
        timeout: 120000,
        reuseExistingServer: !process.env.CI,
      },
});
```

### 11.5.2 Test Fixtures

**fixtures/users.ts**:

```ts
export function uniqueUser() {
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  return {
    email: `test-${id}@example.com`,
    username: `user_${id}`,
    password: "password123",
  };
}
```

**fixtures/helpers.ts**:

```ts
import { Page } from "@playwright/test";
import { uniqueUser } from "./users";

export async function registerUser(page: Page, user = uniqueUser()) {
  await page.goto("/register");
  await page.fill('[name="email"]', user.email);
  await page.fill('[name="username"]', user.username);
  await page.fill('[name="password"]', user.password);
  await page.fill('[name="confirmPassword"]', user.password);
  await page.click('button[type="submit"]');
  await page.waitForURL("/");
  return user;
}

export async function loginUser(page: Page, user: { email: string; password: string }) {
  await page.goto("/login");
  await page.fill('[name="email"]', user.email);
  await page.fill('[name="password"]', user.password);
  await page.click('button[type="submit"]');
  await page.waitForURL("/");
}

export async function addExpense(
  page: Page,
  amount: string,
  category: string,
  date?: string
) {
  await page.click('text=Add Expense');
  await page.fill('[name="amount"]', amount);
  await page.selectOption('[name="category_id"]', { label: category });
  if (date) {
    await page.fill('[name="date"]', date);
  }
  await page.click('button:has-text("Save")');
  await page.waitForSelector('[role="dialog"]', { state: "detached" });
}

export async function setBudget(page: Page, amount: string) {
  await page.goto("/budgets");
  await page.fill('[name="amount"]', amount);
  await page.click('button:has-text("Save")');
  await page.waitForSelector('text=Budget saved');
}
```

### 11.5.3 happy-path.spec.ts

```ts
import { test, expect } from "@playwright/test";
import { registerUser, addExpense, setBudget } from "../fixtures/helpers";

test("complete user flow", async ({ page }) => {
  // 1. Register
  await registerUser(page);

  // 2. Add 3 expenses
  await addExpense(page, "25.50", "Food & Dining");
  await addExpense(page, "60.00", "Groceries");
  await addExpense(page, "15.00", "Transportation");

  // 3. Set budget
  await setBudget(page, "500.00");

  // 4. View dashboard
  await page.goto("/");
  await expect(page.locator('[data-testid="total-spent"]')).toHaveText("$100.50");
  await expect(page.locator('[data-testid="budget-remaining"]')).toHaveText("$399.50");

  // 5. All charts render
  await expect(page.locator('[data-testid="category-pie"]')).toBeVisible();
  await expect(page.locator('[data-testid="monthly-trend"]')).toBeVisible();
  await expect(page.locator('[data-testid="cumulative-line"]')).toBeVisible();
  await expect(page.locator('[data-testid="weekly-heatmap"]')).toBeVisible();
  await expect(page.locator('[data-testid="budget-progress"]')).toBeVisible();

  // 6. Recent transactions show 3 items
  await expect(page.locator('[data-testid="recent-item"]')).toHaveCount(3);

  // 7. Edit an expense
  await page.goto("/expenses");
  await page.locator('[data-testid="expense-row"]').first().locator('[data-testid="edit"]').click();
  await page.fill('[name="amount"]', "50.00");
  await page.click('button:has-text("Save")');

  // 8. Dashboard reflects update
  await page.goto("/");
  await expect(page.locator('[data-testid="total-spent"]')).toHaveText("$125.00");

  // 9. Delete an expense
  await page.goto("/expenses");
  await page.locator('[data-testid="expense-row"]').first().locator('[data-testid="delete"]').click();
  await page.click('button:has-text("Delete")');

  // 10. Dashboard reflects deletion
  await page.goto("/");
  await expect(page.locator('[data-testid="total-spent"]')).toHaveText("$75.00");

  // 11. Logout
  await page.click('[data-testid="user-menu"]');
  await page.click('text=Logout');
  await expect(page).toHaveURL("/login");
});
```

### 11.5.4 isolation.spec.ts

```ts
import { test, expect } from "@playwright/test";
import { registerUser, addExpense } from "../fixtures/helpers";

test("user cannot see other user's data", async ({ browser }) => {
  const ctxA = await browser.newContext();
  const ctxB = await browser.newContext();
  const pageA = await ctxA.newPage();
  const pageB = await ctxB.newPage();

  // User A registers and adds an expense
  await registerUser(pageA);
  await addExpense(pageA, "100.00", "Food & Dining");

  // User A sees the expense
  await pageA.goto("/");
  await expect(pageA.locator('[data-testid="total-spent"]')).toHaveText("$100.00");

  // User B registers
  await registerUser(pageB);

  // User B sees empty dashboard
  await expect(pageB.locator('[data-testid="total-spent"]')).toHaveText("$0.00");
  await pageB.goto("/expenses");
  await expect(pageB.locator('[data-testid="expense-row"]')).toHaveCount(0);

  await ctxA.close();
  await ctxB.close();
});
```

### 11.5.5 month-switch.spec.ts

```ts
import { test, expect } from "@playwright/test";
import { registerUser, addExpense } from "../fixtures/helpers";

test("month switch updates all charts", async ({ page }) => {
  await registerUser(page);

  await addExpense(page, "50.00", "Food & Dining", "2026-10-15");
  await addExpense(page, "30.00", "Groceries", "2026-09-10");

  // Default month is current. Navigate to October 2026.
  await page.goto("/");
  await page.click('[data-testid="month-picker"]');
  await page.fill('[data-testid="month-input"]', "2026-10");

  await expect(page.locator('[data-testid="total-spent"]')).toHaveText("$50.00");

  // Switch to September
  await page.click('[data-testid="prev-month"]');
  await expect(page.locator('[data-testid="total-spent"]')).toHaveText("$30.00");

  // Switch back to October
  await page.click('[data-testid="next-month"]');
  await expect(page.locator('[data-testid="total-spent"]')).toHaveText("$50.00");
});
```

### 11.5.6 E2E Data Isolation Strategy

| Strategy | Implementation |
|---|---|
| Unique users | Each test creates a new user with timestamp + random ID |
| No cleanup | Isolated data does not affect other tests |
| No shared state | Tests run sequentially but do not depend on order |
| Optional cleanup | Documented SQL for manual cleanup |

**Manual cleanup SQL**:

```sql
DELETE FROM audit_logs WHERE user_id IN
  (SELECT id FROM users WHERE email LIKE 'test-%@example.com');
DELETE FROM expenses WHERE user_id IN
  (SELECT id FROM users WHERE email LIKE 'test-%@example.com');
DELETE FROM budgets WHERE user_id IN
  (SELECT id FROM users WHERE email LIKE 'test-%@example.com');
DELETE FROM categories WHERE user_id IN
  (SELECT id FROM users WHERE email LIKE 'test-%@example.com');
DELETE FROM users WHERE email LIKE 'test-%@example.com';
```

## 11.6 Test Execution

### 11.6.1 Makefile Targets

```makefile
test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest -v

test-backend-unit:
	cd backend && uv run pytest tests/unit -v

test-backend-integration:
	cd backend && uv run pytest tests/integration -v

test-backend-cov:
	cd backend && uv run pytest --cov=app --cov-report=html

test-frontend:
	cd frontend && npm run test

test-frontend-cov:
	cd frontend && npm run test -- --coverage

e2e:
	docker compose up -d --build
	cd e2e && npm ci && npx playwright install --with-deps
	cd e2e && npx playwright test
	docker compose down
```

### 11.6.2 CI Execution

| Workflow | Runs |
|---|---|
| ci.yml | `make test-backend`, `make test-frontend` |
| e2e.yml | `make e2e` |

### 11.6.3 Local Execution

```bash
# Backend only
cd backend && uv run pytest

# Frontend only
cd frontend && npm test

# Everything
make test

# E2E
make e2e
```

## 11.7 Test Data Strategy

### 11.7.1 Backend Tests

| Test Type | Data Source |
|---|---|
| Unit | In-memory SQLite, seeded system categories |
| Integration | In-memory SQLite, seeded system categories |
| Test users | Created per test via fixtures |

### 11.7.2 Frontend Tests

| Test Type | Data Source |
|---|---|
| Unit | Pure functions, no data |
| Component | MSW handlers return fixed data |
| Page | MSW handlers with variant responses |

### 11.7.3 E2E Tests

| Test Type | Data Source |
|---|---|
| All | Real backend + database, unique users per test |

### 11.7.4 Why SQLite for Backend Tests

| Reason | Explanation |
|---|---|
| Speed | In-memory, no disk I/O |
| Isolation | Fresh database per test |
| No external dependency | No PostgreSQL needed |
| Same ORM | SQLAlchemy handles the difference |

**Trade-off**: Some PostgreSQL-specific behavior is not tested. The
integration tests verify ORM behavior, not database-specific features.
PostgreSQL is tested in CI via Docker Compose.

## 11.8 What Is Not Tested

| Item | Reason |
|---|---|
| Render deployment | Manual verification via `ops/deployment-health.md` |
| Cold start behavior | Hard to automate reliably |
| UptimeRobot | External service |
| Browser compatibility | Playwright uses Chromium only |
| Load testing | Out of scope |
| Security scanning | Manual, separate from tests |
| Visual regression | Out of scope |
| Accessibility automation | Manual checklist |

## 11.9 Testing Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Backend unit framework | pytest | Standard, fixtures, parametrize |
| Backend integration | pytest + TestClient | FastAPI native |
| Test database | SQLite in-memory | Fast, isolated |
| Frontend test framework | Vitest | Vite-native, fast |
| Component testing | React Testing Library | User-centric queries |
| API mocking | MSW | Network-level, realistic |
| E2E framework | Playwright | Reliable, good DX |
| E2E target | Docker Compose | Matches production |
| E2E data | Unique users per test | No cleanup needed |
| Coverage | Reported, not enforced | Visibility without gate |
| CI test split | CI runs unit + integration | Fast feedback |
| E2E timing | Only on main branch | Saves CI minutes |
| Test isolation | Per-test fixtures | No shared state |
| Decimal testing | Compare Decimal to Decimal | Avoids float comparison |
| Date testing | Fixed dates in tests | Deterministic |
| Error testing | Assert status code and error code | Both matter |
```

---