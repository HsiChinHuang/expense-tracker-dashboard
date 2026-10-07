# Chapter 4: System Architecture

## 4.1 Architecture Overview

The application follows a classic three-tier architecture with an added
agent layer. The three tiers are:

1. **Presentation tier** — React SPA running in the browser
2. **Application tier** — FastAPI backend serving both the API and the static frontend
3. **Data tier** — PostgreSQL in production, SQLite as local and fallback

The agent layer sits alongside the application tier. It uses the same API
as the frontend and shares the same JWT authentication.

### 4.1.1 High-Level Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              React SPA (TypeScript)                     │ │
│  │                                                         │ │
│  │  Pages    Components    Charts    Forms                 │ │
│  │     │          │           │        │                   │ │
│  │     └──────────┴───────────┴────────┘                   │ │
│  │                    │                                     │ │
│  │              API Layer (axios)                           │ │
│  │                    │                                     │ │
│  │              AuthContext + MonthContext                  │ │
│  │              TanStack Query (cache)                      │ │
│  └────────────────────┬───────────────────────────────────┘ │
└───────────────────────┼─────────────────────────────────────┘
                        │ HTTPS
                        │ Bearer JWT
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                     Routers                             │ │
│  │  auth  categories  expenses  budgets  dashboard  health │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │                    Services                             │ │
│  │  auth  category  expense  budget  dashboard  audit      │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │              Auth (JWT + bcrypt)                        │ │
│  │              Audit Logger                               │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │              SQLAlchemy ORM                             │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │              Engine Selection                           │ │
│  │  PostgreSQL (primary)  │  SQLite (fallback)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                        ▲
                        │ JWT via HTTP
                        │
┌───────────────────────┴─────────────────────────────────────┐
│                    Agent Layer                               │
│                                                              │
│  pi-agent + qwen3.8-27b                                     │
│     │                                                        │
│     ├── Skills (agent-capabilities/)                         │
│     ├── Subagents (custom-agent/)                            │
│     ├── Hooks (agent-hooks/)                                 │
│     └── MCP Server (mcp-server/)                             │
│              │                                               │
│              └── HTTP calls to backend API                   │
└─────────────────────────────────────────────────────────────┘
```

### 4.1.2 Development vs Production

**Development**:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Vite dev    │      │  Uvicorn     │      │  PostgreSQL  │
│  server      │─────▶│  (reload)    │─────▶│  (Docker)    │
│  :5173       │      │  :8000       │      │  :5432       │
└──────────────┘      └──────────────┘      └──────────────┘
   Frontend              Backend               Database
   (hot reload)          (hot reload)
```

**Production**:

```
┌──────────────────────────────────────────────────────────┐
│                    Render (free tier)                     │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │            Single Docker Container                   │ │
│  │                                                      │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  FastAPI (uvicorn)                             │ │ │
│  │  │    - Serves /api/v1/*                          │ │ │
│  │  │    - Serves static frontend files              │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                 │
│  ┌──────────────────────▼──────────────────────────────┐ │
│  │  Render PostgreSQL (free, 30-day expiry)            │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  Fallback: SQLite (in-container, temporary)              │
└──────────────────────────────────────────────────────────┘
```

## 4.2 Frontend Architecture

### 4.2.1 Layered Structure

The frontend is organized into six layers:

| Layer | Directory | Responsibility |
|---|---|---|
| Entry | `src/main.tsx`, `src/App.tsx` | Bootstrap, provider nesting, routing |
| Pages | `src/pages/` | Route-level components |
| Components | `src/components/` | Reusable UI, charts, forms, layout |
| Hooks | `src/hooks/` | Data fetching and mutations via React Query |
| Context | `src/context/` | Auth and Month global state |
| API | `src/api/` | Centralized HTTP client and resource modules |
| Utils | `src/utils/` | Formatting, date helpers, validation schemas |
| Types | `src/types/` | TypeScript types for API and domain |

### 4.2.2 Data Flow

```
User Action
    │
    ▼
Page Component
    │
    ├── Reads from Context (Auth, Month)
    │
    ├── Calls Hook (useExpenses, useDashboard, etc.)
    │       │
    │       ▼
    │   React Query
    │       │
    │       ├── Cache hit? → Return cached data
    │       │
    │       └── Cache miss? → Call API module
    │                           │
    │                           ▼
    │                       axios client
    │                           │
    │                           ├── Attach JWT from localStorage
    │                           │
    │                           └── Send request to backend
    │
    ▼
Renders UI (loading / error / data state)
```

### 4.2.3 State Ownership

| State Type | Owned By | Persisted In |
|---|---|---|
| Authenticated user | AuthContext | localStorage (token only) |
| Selected month | MonthContext | React state (resets on refresh) |
| Server data | React Query cache | In-memory |
| Form state | React Hook Form | Component-local |
| UI state (modal open, etc.) | Component-local | React state |

### 4.2.4 Provider Nesting

```
QueryClientProvider
  └── BrowserRouter
        └── AuthProvider
              └── MonthProvider
                    └── ToastProvider
                          └── App (routes)
```

**Rationale**: Each provider depends only on its ancestors. QueryClient is
outermost because Auth depends on it. Toast is innermost because any
component may trigger a toast.

## 4.3 Backend Architecture

### 4.3.1 Layered Structure

| Layer | Directory | Responsibility |
|---|---|---|
| Entry | `app/main.py` | App factory, middleware, router mounting, startup events |
| Config | `app/config.py` | Settings loaded from environment |
| Database | `app/database.py` | Engine creation, session factory, fallback logic |
| Routers | `app/routers/` | Request parsing, response shaping |
| Services | `app/services/` | Business logic, transactions, audit |
| Models | `app/models/` | SQLAlchemy ORM definitions |
| Schemas | `app/schemas/` | Pydantic request and response validation |
| Auth | `app/auth/` | JWT signing, verification, password hashing |
| Audit | `app/audit/` | Audit log writer |
| Core | `app/core/` | Errors, logging, shared utilities |

### 4.3.2 Request Lifecycle

```
HTTP Request
    │
    ▼
FastAPI middleware (CORS, request ID)
    │
    ▼
Router endpoint
    │
    ├── Parse path/query/body via Pydantic schema
    │
    ├── Resolve dependencies (get_db, get_current_user)
    │       │
    │       └── get_current_user:
    │             1. Extract Bearer token
    │             2. Decode JWT (signature, exp, aud, iss)
    │             3. Load user from database
    │             4. Return user or raise 401
    │
    ▼
Service method
    │
    ├── Business logic
    │
    ├── Database queries (filtered by user_id)
    │
    ├── Audit log write (same transaction)
    │
    └── Commit transaction
    │
    ▼
Response schema
    │
    ▼
HTTP Response (JSON)
```

### 4.3.3 Dependency Injection

FastAPI dependencies are used for:

| Dependency | Purpose |
|---|---|
| `get_db` | Provides a SQLAlchemy session per request |
| `get_current_user` | Decodes JWT and loads user |
| `get_settings` | Provides cached Settings object |
| `get_audit_logger` | Provides audit logger instance |

### 4.3.4 Transaction Boundaries

- Each request runs in one database session
- Service methods commit at the end
- Audit log write is part of the same transaction
- If audit write fails, the business operation is rolled back
- Read-only endpoints do not commit

### 4.3.5 Error Handling

| Exception | Handler | HTTP Status |
|---|---|---|
| `AppError` | Custom handler | Defined per error |
| `RequestValidationError` | FastAPI default | 422 |
| `HTTPException` | FastAPI default | Defined per raise |
| `SQLAlchemyError` | Custom handler | 503 |
| Unhandled `Exception` | Custom handler | 500 |

All error responses use the same shape:

```json
{
  "detail": "Human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "field": "optional_field_name"
}
```

## 4.4 Data Flow Diagrams

### 4.4.1 Login Flow

```
┌────────┐    ┌──────────┐    ┌────────┐    ┌────────────┐
│ User   │    │ Frontend │    │ Backend│    │ Database   │
└───┬────┘    └────┬─────┘    └───┬────┘    └─────┬──────┘
    │              │              │               │
    │ Enter creds  │              │               │
    ├─────────────▶│              │               │
    │              │ POST /login  │               │
    │              ├─────────────▶│               │
    │              │              │ SELECT user   │
    │              │              ├──────────────▶│
    │              │              │◀──────────────┤
    │              │              │ bcrypt verify │
    │              │              │               │
    │              │              │ Sign JWT      │
    │              │◀─────────────┤               │
    │              │ {token,user} │               │
    │◀─────────────┤              │               │
    │  Redirect    │              │               │
    │  to /        │              │               │
```

### 4.4.2 Create Expense Flow

```
┌────────┐    ┌──────────┐    ┌────────┐    ┌────────────┐
│ User   │    │ Frontend │    │ Backend│    │ Database   │
└───┬────┘    └────┬─────┘    └───┬────┘    └─────┬──────┘
    │              │              │               │
    │ Fill form    │              │               │
    ├─────────────▶│              │               │
    │              │ POST /expenses               │
    │              │ Bearer JWT   │               │
    │              ├─────────────▶│               │
    │              │              │ Verify JWT    │
    │              │              │ Validate body │
    │              │              │ Check category│
    │              │              ├──────────────▶│
    │              │              │◀──────────────┤
    │              │              │ INSERT expense│
    │              │              │ INSERT audit  │
    │              │              │ COMMIT        │
    │              │◀─────────────┤               │
    │              │ 201 + expense│               │
    │              │ Invalidate   │               │
    │              │ cache        │               │
    │◀─────────────┤              │               │
    │ See updated  │              │               │
    │ list         │              │               │
```

### 4.4.3 Dashboard Load Flow

```
┌──────────┐    ┌────────┐    ┌────────────────┐
│ Frontend │    │ Backend│    │ Database       │
└────┬─────┘    └───┬────┘    └────────┬───────┘
     │              │                  │
     │ 6 parallel requests:            │
     │  - summary                      │
     │  - by-category                  │
     │  - trend                        │
     │  - cumulative                   │
     │  - heatmap                      │
     │  - recent                       │
     ├─────────────▶│                  │
     │              │ 6 queries        │
     │              ├─────────────────▶│
     │              │◀─────────────────┤
     │              │ Aggregate in     │
     │              │ Python where     │
     │              │ needed           │
     │◀─────────────┤                  │
     │ Render 5     │                  │
     │ charts       │                  │
```

### 4.4.4 Database Fallback Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ App Startup  │    │ PostgreSQL   │    │ SQLite       │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       │ Try connect       │                   │
       │ (5s timeout)      │                   │
       ├──────────────────▶│                   │
       │                   │                   │
       │  Connection OK?   │                   │
       │                   │                   │
       ├─── Yes ──────────▶│                   │
       │    Use Postgres   │                   │
       │                                       │
       ├─── No ───────────────────────────────▶│
       │    Log WARNING                        │
       │    Create tables                      │
       │    Seed categories                    │
       │    Use SQLite                         │
       │                                       │
       │ Health check reports                  │
       │ fallback_active = true                │
```

## 4.5 Authentication Flow

### 4.5.1 JWT Structure

```json
{
  "sub": "user-uuid",
  "iss": "expense-tracker",
  "aud": "expense-tracker-api",
  "exp": 1729000000,
  "iat": 1728998200,
  "type": "access"
}
```

### 4.5.2 Token Validation Steps

Every protected request goes through these steps:

1. Extract `Authorization: Bearer <token>` header
2. Decode JWT with fixed algorithm `HS256`
3. Verify signature with `JWT_SECRET`
4. Verify `exp` (not expired)
5. Verify `aud` matches `expense-tracker-api`
6. Verify `iss` matches `expense-tracker`
7. Extract `sub` as user_id
8. Load user from database
9. Verify `user.is_active == true`
10. Attach user to request state

Any failure returns 401 with a specific error code.

### 4.5.3 Token Storage

- **Frontend**: stored in `localStorage` under key `token`
- **Sent as**: `Authorization: Bearer <token>` header
- **Expiry**: 24 hours
- **No refresh token** in MVP

**Trade-off**: localStorage is vulnerable to XSS. HttpOnly cookies would be
safer but require CSRF protection. For this project, localStorage is
acceptable because:
- No third-party scripts
- Strict Content Security Policy
- Documented in `security/agent-security-notes.md`

## 4.6 Directory Structure Overview

### 4.6.1 Repository Root

```
expense-tracker-dashboard/
├── README.md
├── product-spec.md
├── AGENTS.md
├── CLAUDE.md
├── openapi.yaml
├── docker-compose.yml
├── render.yaml
├── Makefile
├── .env.example
├── .gitignore
├── LICENSE
├── Dockerfile
├── .github/
├── frontend/
├── backend/
├── e2e/
├── docs/
├── security/
├── ops/
├── agent-capabilities/
├── agent-hooks/
├── mcp-server/
├── custom-agent/
└── screenshots/
```

### 4.6.2 Frontend

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   ├── charts/
│   │   ├── forms/
│   │   └── common/
│   ├── pages/
│   ├── hooks/
│   ├── context/
│   ├── types/
│   ├── utils/
│   └── test/
├── public/
├── package.json
├── vite.config.ts
├── vitest.config.ts
├── tailwind.config.js
├── tsconfig.json
└── Dockerfile
```

### 4.6.3 Backend

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── auth/
│   ├── audit/
│   └── core/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

### 4.6.4 Agent Layer

```
agent-capabilities/
├── monthly-report/SKILL.md
├── add-expense/SKILL.md
└── budget-check/SKILL.md

agent-hooks/
├── validate-amount.py
├── validate-ownership.py
└── README.md

mcp-server/
├── server.py
├── auth.py
├── config.py
├── tools/
│   ├── add_expense.py
│   ├── get_budget_status.py
│   ├── monthly_summary.py
│   └── list_expenses.py
├── pyproject.toml
└── README.md

custom-agent/
├── finance-analyst.md
└── qa-reviewer.md

.agents/
├── skills/ → symlink to agent-capabilities/
└── agents/ → symlink to custom-agent/
```

### 4.6.5 Documentation and Artifacts

```
docs/
├── architecture.md
├── api.md
├── process.md
├── ai-workflow.md
├── design-system.md
├── testing-guidelines.md
├── agent-extension-pack.md
├── permissions.md
├── task-template.md
└── team/
    ├── pm.md
    ├── software-engineer.md
    └── qa-engineer.md

security/
├── pr-audit.md
├── gitleaks-report.json
├── semgrep-report.json
├── trivy-report.json
├── pip-audit-report.txt
├── npm-audit-report.txt
├── agent-security-notes.md
└── ai-tool-data-policy.md

ops/
├── runbook.md
├── health-check.md
├── diagnosis.md
├── logging.md
└── deployment-health.md
```

## 4.7 Cross-Cutting Concerns

### 4.7.1 Logging

| Concern | Implementation |
|---|---|
| Format | JSON structured |
| Level | INFO in production, DEBUG in development |
| Request ID | Generated per request, included in all logs |
| Sensitive data | Never logged (passwords, tokens, full bodies) |
| Key events | Auth, expense, budget, db fallback |

### 4.7.2 Configuration

| Source | Priority |
|---|---|
| Environment variables | Highest |
| `.env` file | Medium (development only) |
| Default values in `config.py` | Lowest |

### 4.7.3 Error Handling

| Layer | Responsibility |
|---|---|
| Router | Raise `AppError` or `HTTPException` |
| Service | Raise `AppError` for business rule violations |
| Database | Caught and translated to 503 |
| Frontend axios | Normalize errors into a consistent shape |
| Frontend UI | Show field errors, toasts, or redirects |

### 4.7.4 Security

| Concern | Implementation |
|---|---|
| Password storage | bcrypt with salt |
| Token signing | HS256 with secret from env |
| Token validation | Signature, exp, aud, iss |
| User isolation | Every query filtered by user_id |
| Cross-user access | Returns 404 (does not reveal existence) |
| Secrets | Never committed, `.env` in `.gitignore` |
| Audit | All writes logged in same transaction |

### 4.7.5 Testing

| Layer | Tool | Location |
|---|---|---|
| Backend unit | pytest | `backend/tests/unit/` |
| Backend integration | pytest + httpx | `backend/tests/integration/` |
| Frontend unit | Vitest | `frontend/src/**/*.test.ts` |
| Frontend component | Vitest + RTL | `frontend/src/**/*.test.tsx` |
| E2E | Playwright | `e2e/tests/` |

## 4.8 Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend serves API calls from one layer | `src/api/` | Single point of integration, easy to mock |
| Backend serves frontend static files | FastAPI StaticFiles | Single container, simpler deployment |
| Database abstraction via SQLAlchemy | SQLAlchemy 2.0 | Supports both PostgreSQL and SQLite |
| Automatic SQLite fallback | On startup only | Keeps app functional when PostgreSQL unavailable |
| JWT in localStorage | Not HttpOnly cookie | Simpler, acceptable for this scope |
| No refresh token | 24-hour access token | Simpler; documented trade-off |
| Single container in production | Frontend built into backend image | Simpler Render config |
| Agent layer uses same API | HTTP + JWT | No special backend endpoints for agents |
| Audit in same transaction | Service layer | Atomicity guarantee |
| Month selector in context | MonthContext | Global chart synchronization |

## 4.9 Constraints and Assumptions

### 4.9.1 Constraints

- Render free tier: 512 MB RAM, 0.1 CPU, 15-minute idle sleep
- Render free PostgreSQL: 1 GB storage, 30-day expiry
- Single container deployment: no separate frontend service
- SQLite fallback: data not persisted across restarts
- No rate limiting in MVP
- No horizontal scaling
- No caching layer beyond React Query

### 4.9.2 Assumptions

- Users have stable internet connectivity
- Users access the app through a modern browser (Chrome, Firefox, Safari, Edge)
- Traffic volume is low (demo and peer review)
- Data volume per user is small (hundreds of expenses)
- The agent layer runs on the developer's local machine

### 4.9.3 Known Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| Cold start on Render | First request slow | UptimeRobot ping |
| PostgreSQL 30-day expiry | Data loss mid-review | SQLite fallback |
| No refresh token | User must re-login after 24h | Documented |
| No rate limiting | Brute-force possible | Documented |
| localStorage JWT | XSS vulnerable | No third-party scripts |
| SQLite fallback data loss | Temporary data only | Documented in README |
| No connection pooling for SQLite | Slower under load | Acceptable for demo |
```

---