# Expense Tracker & Budget Dashboard — Requirements

Version: 1.0.0
Status: Draft
Last updated: 2026-10-07

---

## Part 1: Documentation Notes

### 1. Document Purpose

This document is the consolidated requirements specification for the
Expense Tracker & Budget Dashboard project. It is the single entry
point for understanding what the system must do, how it must be
built, and how each requirement is verified.

This document is:

- A requirements index
- A traceability map from requirements to source chapters
- A verification guide for peer reviewers

This document is not:

- A replacement for the detailed chapter documents
- A duplicate of code, schemas, or test files
- A marketing description of the project

Each requirement is stated in checkable form and linked to the
chapter and section where the full detail lives.

### 2. Document Scope

This document covers the 17 chapters that make up the project
specification. It does not include Chapter 18 (deferred).

All chapter references use the path convention:

```
requirements/ChapterX_Name.md
```

For example:

- `requirements/Chapter1_ProjectOverview.md`
- `requirements/Chapter9_AIWorkflow.md`
- `requirements/Chapter14_CICDandDeployment.md`

Section references use the format `§X.Y.Z`, matching the headings in
the source chapter.

### 3. Requirement Identification Rules

#### 3.1 Requirement ID Format

```
REQ-<DOMAIN>-<NNN>
```

| Part | Meaning | Example |
|---|---|---|
| REQ | Fixed prefix | REQ |
| DOMAIN | Short uppercase domain code | AUTH |
| NNN | Three-digit sequence within the domain | 001 |

Full example: `REQ-AUTH-001`

#### 3.2 Domain Codes

| Domain Code | Area | Source Chapter |
|---|---|---|
| PROJ | Project overview | Chapter 1 |
| PROD | Product specification | Chapter 2 |
| TECH | Tech stack | Chapter 3 |
| ARCH | System architecture | Chapter 4 |
| DB | Database design | Chapter 5 |
| BE | Backend design | Chapter 6 |
| API | API contract | Chapter 7 |
| FE | Frontend design | Chapter 8 |
| AI | AI workflow | Chapter 9 |
| EXT | Agent extension pack | Chapter 10 |
| TEST | Testing strategy | Chapter 11 |
| SEC | Security and audit | Chapter 12 |
| OPS | Operations | Chapter 13 |
| CICD | CI/CD and deployment | Chapter 14 |
| DOC | Documentation | Chapter 15 |
| STRUCT | Project structure | Chapter 16 |
| PLAN | Development plan | Chapter 17 |

#### 3.3 Requirement Structure

Each requirement entry uses this structure:

```markdown
### REQ-<DOMAIN>-<NNN>: <Short title>

**Statement**: One or two sentences describing what must be true.

**Source**: `requirements/ChapterX_Name.md §X.Y.Z`

**Verification**: How a reviewer confirms the requirement is met.

**Priority**: Must / Should / Could
```

#### 3.4 Priority Definitions

| Priority | Meaning |
|---|---|
| Must | Required for the project to be considered complete |
| Should | Strongly recommended; omission weakens the submission |
| Could | Optional improvement; not required for MVP |

### 4. Glossary

| Term | Definition | Source |
|---|---|---|
| MVP | Minimum Viable Product; the smallest complete version | Chapter 1 §1.6 |
| SQLite fallback | Automatic switch to SQLite when PostgreSQL is unreachable | Chapter 5 §5.13 |
| Agent Extension Pack | Skills, hooks, MCP server, subagents, and permissions | Chapter 10 §10.1 |
| PM agent | Product Manager role that grooms issues | Chapter 9 §9.4.1 |
| SWE agent | Software Engineer role that implements issues | Chapter 9 §9.4.2 |
| QA agent | Quality Assurance role that verifies issues | Chapter 9 §9.4.3 |
| MCP | Model Context Protocol; exposes tools to the agent | Chapter 9 §9.9 |
| Hook | Guardrail that validates inputs before an action | Chapter 10 §10.3 |
| Skill | Reusable procedure the agent can discover and run | Chapter 10 §10.2 |
| Subagent | Specialized agent with a separate context | Chapter 10 §10.5 |
| Orchestrator | Main session that enforces the PM → SWE → QA graph | Chapter 9 §9.5 |
| Loop engineering | Running an agent repeatedly until a stop condition | Chapter 9 §9.5.5 |
| Graph engineering | Multi-agent workflow with specialized roles | Chapter 9 §9.5.6 |
| Decimal | Exact decimal type used for all money values | Chapter 5 §5.11 |
| year_month | String in YYYY-MM format, used as budget key | Chapter 5 §5.6 |
| Audit log | Record of every write to expenses and budgets | Chapter 5 §5.7 |
| Fallback | See SQLite fallback | Chapter 5 §5.13 |
| Cold start | Delay when Render free tier wakes from sleep | Chapter 14 §14.5 |
| Criteria mapping | Table matching Final Project criteria to evidence | Chapter 15 §15.10 |

---

## Part 2: Project-Level Requirements

### 5. Project Overview Requirements

**Source**: `requirements/Chapter1_ProjectOverview.md`

#### REQ-PROJ-001: Product identity

**Statement**: The project is named "Expense Tracker & Budget Dashboard",
the repository is named `expense-tracker-dashboard`, and the license
is MIT.

**Source**: `Chapter1_ProjectOverview.md §1.1`

**Verification**: Read `README.md` and `LICENSE`.

**Priority**: Must

#### REQ-PROJ-002: One-line description

**Statement**: The project has a one-line description stating that
users record expenses, set monthly budgets, and view spending insights
through an interactive dashboard with five visualizations.

**Source**: `Chapter1_ProjectOverview.md §1.2`

**Verification**: Read the top of `README.md`.

**Priority**: Must

#### REQ-PROJ-003: Target users

**Statement**: The application targets individuals managing personal
finances, single-currency (USD) users, and users who do not need
shared budgets.

**Source**: `Chapter1_ProjectOverview.md §1.3`

**Verification**: Read `README.md` and `product-spec.md`.

**Priority**: Must

#### REQ-PROJ-004: Core questions answered

**Statement**: The application answers three questions: how much have
I spent this month, how much budget is left, and where is my money
going. It answers them visually, not just numerically.

**Source**: `Chapter1_ProjectOverview.md §1.4`

**Verification**: Use the live app; observe KPI cards and five charts.

**Priority**: Must

#### REQ-PROJ-005: Final Project criteria mapping

**Statement**: The README contains a table mapping all 14 Final Project
criteria to evidence in the repository.

**Source**: `Chapter1_ProjectOverview.md §1.5`

**Verification**: Read the "Final Project Criteria Mapping" section in
`README.md`.

**Priority**: Must

#### REQ-PROJ-006: In-scope capabilities

**Statement**: The MVP includes authentication, expenses, budgets,
categories, dashboard with five visualizations, data integrity, SQLite
fallback, Agent Extension Pack, security and audit artifacts, and
Render deployment.

**Source**: `Chapter1_ProjectOverview.md §1.6`

**Verification**: Read the "In Scope" section; verify each capability
exists in the repository.

**Priority**: Must

#### REQ-PROJ-007: Out-of-scope boundaries

**Statement**: Multi-currency, income tracking, bank integration,
shared budgets, mobile app, recurring expenses, receipt upload, email
verification, password reset, dark mode, refresh tokens, OAuth, bulk
delete, rate limiting, admin role, Kubernetes, managed database, VPC,
multi-region, load balancing, WebSocket, push notifications, data
export, and i18n are explicitly out of scope.

**Source**: `Chapter1_ProjectOverview.md §1.6`

**Verification**: Read the "Out of Scope" section; confirm none are
implemented.

**Priority**: Must

#### REQ-PROJ-008: Project constraints

**Statement**: The project uses USD only, monthly total budget per
user, JWT with bcrypt, 24-hour token lifetime, 8-character minimum
password, 3-50 character username, optional note up to 500 characters,
2-decimal amount precision, and 20-item default pagination.

**Source**: `Chapter1_ProjectOverview.md §1.7`

**Verification**: Read the constraints table; spot-check against code.

**Priority**: Must

#### REQ-PROJ-009: Success criteria

**Statement**: The project is successful when all 14 criteria have
evidence, the app is deployed, all tests pass, a new user can complete
the core flow, user isolation is verified, SQLite fallback works, the
Agent Extension Pack is functional, security artifacts are present, a
reviewer can reproduce setup in under 10 minutes, and the README
provides a 5-minute verification path.

**Source**: `Chapter1_ProjectOverview.md §1.8`

**Verification**: Use the acceptance checklist (Part 9 of this
document).

**Priority**: Must

---

### 6. Product Specification Requirements

**Source**: `requirements/Chapter2_ProductSpecification.md`

#### 6.1 Problem and Users

##### REQ-PROD-001: Problem statement

**Statement**: The product-spec documents that spreadsheets are
tedious and full accounting software is overwhelming, and that the
product fills the gap with a focused expense tracker and budget
dashboard.

**Source**: `Chapter2_ProductSpecification.md §2.1`

**Verification**: Read `product-spec.md §Problem Statement`.

**Priority**: Must

##### REQ-PROD-002: User stories for authentication

**Statement**: User stories AUTH-1 through AUTH-5 exist for
registration, login, profile, logout, and isolation.

**Source**: `Chapter2_ProductSpecification.md §2.2`

**Verification**: Read `product-spec.md §User Stories`.

**Priority**: Must

##### REQ-PROD-003: User stories for expenses

**Statement**: User stories EXP-1 through EXP-7 exist for create,
list, filter, update, delete, isolation, and validation.

**Source**: `Chapter2_ProductSpecification.md §2.2`

**Verification**: Read `product-spec.md §User Stories`.

**Priority**: Must

##### REQ-PROD-004: User stories for budgets

**Statement**: User stories BUD-1 through BUD-5 exist for set, update,
delete, view, and duplicate conflict.

**Source**: `Chapter2_ProductSpecification.md §2.2`

**Verification**: Read `product-spec.md §User Stories`.

**Priority**: Must

##### REQ-PROD-005: User stories for categories

**Statement**: User stories CAT-1 through CAT-5 exist for system
categories, custom categories, combined view, protection of system
categories, and duplicate name handling.

**Source**: `Chapter2_ProductSpecification.md §2.2`

**Verification**: Read `product-spec.md §User Stories`.

**Priority**: Must

##### REQ-PROD-006: User stories for dashboard

**Statement**: User stories DASH-1 through DASH-10 exist for KPI
cards, five charts, month switch, and empty state.

**Source**: `Chapter2_ProductSpecification.md §2.2`

**Verification**: Read `product-spec.md §User Stories`.

**Priority**: Must

##### REQ-PROD-007: User stories for audit

**Statement**: User stories AUD-1 through AUD-3 exist for logging
expense writes, logging budget writes, and no API access to audit
logs.

**Source**: `Chapter2_ProductSpecification.md §2.2`

**Verification**: Read `product-spec.md §User Stories`.

**Priority**: Must

#### 6.2 Functional Requirements

##### REQ-PROD-010: Authentication functional requirements

**Statement**: FR-AUTH-1 through FR-AUTH-4 define registration, login,
current user, and logout behavior, including validation rules and
error codes.

**Source**: `Chapter2_ProductSpecification.md §2.3.1`

**Verification**: Read `product-spec.md §Functional Requirements`;
run auth integration tests.

**Priority**: Must

##### REQ-PROD-011: Expense functional requirements

**Statement**: FR-EXP-1 through FR-EXP-5 define expense create, list,
get, update, and delete, including validation, user isolation, and
audit behavior.

**Source**: `Chapter2_ProductSpecification.md §2.3.2`

**Verification**: Read `product-spec.md §Functional Requirements`;
run expense integration tests.

**Priority**: Must

##### REQ-PROD-012: Budget functional requirements

**Statement**: FR-BUD-1 through FR-BUD-3 define budget set (upsert),
get (returns 0 if absent), and delete, including audit behavior.

**Source**: `Chapter2_ProductSpecification.md §2.3.3`

**Verification**: Read `product-spec.md §Functional Requirements`;
run budget integration tests.

**Priority**: Must

##### REQ-PROD-013: Category functional requirements

**Statement**: FR-CAT-1 through FR-CAT-3 define category list, create,
and system category protection.

**Source**: `Chapter2_ProductSpecification.md §2.3.4`

**Verification**: Read `product-spec.md §Functional Requirements`;
run category integration tests.

**Priority**: Must

##### REQ-PROD-014: Dashboard functional requirements

**Statement**: FR-DASH-1 through FR-DASH-6 define summary, by-category,
trend, cumulative, heatmap, and recent behavior, including edge cases.

**Source**: `Chapter2_ProductSpecification.md §2.3.5`

**Verification**: Read `product-spec.md §Functional Requirements`;
run dashboard integration tests.

**Priority**: Must

##### REQ-PROD-015: Audit functional requirements

**Statement**: FR-AUD-1 and FR-AUD-2 define that audit logs are
written in the same transaction as the business operation and that no
API endpoint exposes them.

**Source**: `Chapter2_ProductSpecification.md §2.3.6`

**Verification**: Read `product-spec.md §Functional Requirements`;
inspect `audit_logs` table after operations; confirm no audit router.

**Priority**: Must

##### REQ-PROD-016: Health check functional requirement

**Statement**: FR-HEALTH-1 defines a public health endpoint returning
status, database, fallback_active, and version.

**Source**: `Chapter2_ProductSpecification.md §2.3.7`

**Verification**: `curl /api/v1/health`; check response fields.

**Priority**: Must

##### REQ-PROD-017: Database fallback functional requirement

**Statement**: FR-DB-1 defines automatic fallback to SQLite within 5
seconds when PostgreSQL is unreachable at startup, with table creation
and category seeding, and notes that data written during fallback is
temporary.

**Source**: `Chapter2_ProductSpecification.md §2.3.8`

**Verification**: Follow `ops/diagnosis.md`; observe fallback logs and
health response.

**Priority**: Must

#### 6.3 Non-Functional Requirements

##### REQ-PROD-020: Performance targets

**Statement**: Dashboard loads in under 2 seconds on warm cache, simple
API queries under 200ms, dashboard aggregations under 500ms, cold
start under 60 seconds, and frontend initial load under 3 seconds.

**Source**: `Chapter2_ProductSpecification.md §2.4.1`

**Verification**: Measure with browser dev tools and `curl -w`.

**Priority**: Should

##### REQ-PROD-021: Reliability

**Statement**: SQLite fallback keeps the app functional when
PostgreSQL is unavailable; health check reports database status; no
data loss on graceful restart when using PostgreSQL; audit log is
atomic with the business operation.

**Source**: `Chapter2_ProductSpecification.md §2.4.2`

**Verification**: Follow `ops/diagnosis.md`; inspect audit log write.

**Priority**: Must

##### REQ-PROD-022: Security non-functional requirements

**Statement**: Passwords are bcrypt-hashed, JWT uses fixed HS256 and
validates signature, expiry, audience, issuer, all queries filter by
user_id, cross-user access returns 404, secrets come from environment
variables, `.env` is gitignored, and audit log records all writes.

**Source**: `Chapter2_ProductSpecification.md §2.4.3`

**Verification**: Read `security/agent-security-notes.md`; run
isolation tests; inspect JWT config.

**Priority**: Must

##### REQ-PROD-023: Data integrity

**Statement**: Amounts are NUMERIC(12,2) and handled as Decimal,
transmitted as strings; dates use DATE without timezone; budget has a
unique constraint on (user_id, year_month); foreign keys and CHECK
constraints are enforced.

**Source**: `Chapter2_ProductSpecification.md §2.4.4`

**Verification**: Inspect models and migrations; run Decimal tests.

**Priority**: Must

##### REQ-PROD-024: Usability

**Statement**: Dashboard loads in under 2 seconds, empty and loading
states are shown, error messages are specific, month selector updates
all charts, forms validate before submit, destructive actions have
confirmation dialogs, and the layout is responsive.

**Source**: `Chapter2_ProductSpecification.md §2.4.5`

**Verification**: Manual walkthrough; inspect components.

**Priority**: Should

##### REQ-PROD-025: Accessibility

**Statement**: Form inputs have labels, buttons have accessible names,
modal has role and focus trap, charts have descriptions, contrast is
at least 4.5:1, keyboard navigation works, skip link exists, each route
has a unique title, and `html lang="en"`.

**Source**: `Chapter2_ProductSpecification.md §2.4.6`

**Verification**: Manual a11y check; inspect components.

**Priority**: Should

##### REQ-PROD-026: Maintainability

**Statement**: Backend is split into routers, services, models,
schemas; frontend into api, components, pages, hooks, context, utils;
all API calls are centralized; all business logic is in services;
tests exist at unit, integration, and E2E levels; docs live in
`docs/`; AGENTS.md provides agent context.

**Source**: `Chapter2_ProductSpecification.md §2.4.7`

**Verification**: Inspect directory structure.

**Priority**: Must

##### REQ-PROD-027: Portability

**Statement**: Docker Compose runs the full stack on any platform;
SQLite is used locally and PostgreSQL in production; all configuration
is via environment variables; no hardcoded paths or credentials.

**Source**: `Chapter2_ProductSpecification.md §2.4.8`

**Verification**: `docker compose up --build`; inspect `.env.example`.

**Priority**: Must

##### REQ-PROD-028: Observability

**Statement**: Logs are structured JSON; key events (auth, expense,
budget, db fallback) are logged; health check exists; audit log lives
in the database; Render logs are accessible.

**Source**: `Chapter2_ProductSpecification.md §2.4.9`

**Verification**: Read `ops/logging.md`; inspect log output.

**Priority**: Must

#### 6.4 Edge Cases

##### REQ-PROD-030: Authentication edge cases

**Statement**: Edge cases for invalid email, short password, short
username, spaces in username, duplicate email, duplicate username,
wrong password, nonexistent email, expired token, invalid signature,
alg=none, missing token, and disabled user are all defined.

**Source**: `Chapter2_ProductSpecification.md §2.5.1`

**Verification**: Run auth integration tests.

**Priority**: Must

##### REQ-PROD-031: Expense edge cases

**Statement**: Edge cases for zero amount, negative amount, three
decimals, over-max amount, empty amount, missing category, other
user's category, invalid date, long note, cross-user update and
delete, invalid pagination, and empty filters are all defined.

**Source**: `Chapter2_ProductSpecification.md §2.5.2`

**Verification**: Run expense integration tests.

**Priority**: Must

##### REQ-PROD-032: Budget edge cases

**Statement**: Edge cases for invalid year_month, duplicate budget,
upsert on nonexistent, absent budget returns 0, negative amount, and
delete nonexistent are defined.

**Source**: `Chapter2_ProductSpecification.md §2.5.3`

**Verification**: Run budget integration tests.

**Priority**: Must

##### REQ-PROD-033: Dashboard edge cases

**Statement**: Edge cases for empty month, no budget, expenses without
budget, exactly at budget, month boundary, year boundary, heatmap
crossing year boundary, more than 6 categories, exactly 6 categories,
zero expenses in trend, cumulative last point equals total, and
recent transaction limits are defined.

**Source**: `Chapter2_ProductSpecification.md §2.5.4`

**Verification**: Run dashboard integration tests.

**Priority**: Must

##### REQ-PROD-034: Category edge cases

**Statement**: Edge cases for duplicate system name, duplicate own
name, long name, invalid HEX, delete system category, and update
system category are defined.

**Source**: `Chapter2_ProductSpecification.md §2.5.5`

**Verification**: Run category integration tests.

**Priority**: Must

##### REQ-PROD-035: Database edge cases

**Statement**: Edge cases for PostgreSQL unreachable at startup,
unreachable at runtime, recovery requiring restart, unwritable SQLite
file, migration failure, and concurrent budget creation are defined.

**Source**: `Chapter2_ProductSpecification.md §2.5.6`

**Verification**: Follow `ops/diagnosis.md`; inspect logs.

**Priority**: Must

##### REQ-PROD-036: Frontend edge cases

**Statement**: Edge cases for token expiry during session, network
error, empty dashboard, loading state, invalid form data, protected
route without login, rapid month switching, browser back after
logout, and long note text are defined.

**Source**: `Chapter2_ProductSpecification.md §2.5.7`

**Verification**: Manual walkthrough; frontend tests.

**Priority**: Should

#### 6.5 Success Criteria

##### REQ-PROD-040: Functional success

**Statement**: A new user can register, log in, record expenses, set
a budget, and view the dashboard without errors; all five charts
render; month switching updates all charts; user isolation holds;
system categories are always available; custom categories can be
created; audit log records all writes.

**Source**: `Chapter2_ProductSpecification.md §2.6.1`

**Verification**: E2E tests; manual walkthrough.

**Priority**: Must

##### REQ-PROD-041: Technical success

**Statement**: All unit, integration, and E2E tests pass; SQLite
fallback works; health check is accurate; CI runs on every PR; CD
deploys on merge to main; a public URL is available.

**Source**: `Chapter2_ProductSpecification.md §2.6.2`

**Verification**: Check CI status; open the live URL.

**Priority**: Must

##### REQ-PROD-042: Quality success

**Statement**: README provides a 5-minute verification path; all 14
criteria have evidence; security artifacts are present; Agent
Extension Pack is functional; AI workflow is documented with real
sessions; a reviewer can reproduce setup in under 10 minutes.

**Source**: `Chapter2_ProductSpecification.md §2.6.3`

**Verification**: Follow the peer review checklist.

**Priority**: Must

##### REQ-PROD-043: Measurable targets

**Statement**: Backend test count >= 50, frontend test count >= 20,
E2E test count >= 3, API endpoints >= 15, dashboard charts = 5,
system categories = 10, security artifacts = 8, ops artifacts = 5,
agent skills = 3, agent subagents = 2, MCP tools = 4, agent hooks = 2,
documentation files >= 20, README < 500 lines, setup time < 10
minutes, cold start < 60 seconds.

**Source**: `Chapter2_ProductSpecification.md §2.6.4`

**Verification**: Count each item; run timing measurements.

**Priority**: Should

---

## Part 3: Technical Requirements

### 7. Tech Stack Requirements

**Source**: `requirements/Chapter3_TechStack.md`

#### 7.1 Frontend Stack

##### REQ-TECH-001: Frontend framework

**Statement**: The frontend uses React 18 with TypeScript 5, built
with Vite 5.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/package.json`.

**Priority**: Must

##### REQ-TECH-002: Frontend routing

**Statement**: The frontend uses React Router v6 for client-side
routing with nested routes and route guards.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/src/App.tsx`.

**Priority**: Must

##### REQ-TECH-003: Frontend styling

**Statement**: The frontend uses Tailwind CSS 3 for styling, with no
runtime CSS-in-JS.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/tailwind.config.js` and component
files.

**Priority**: Must

##### REQ-TECH-004: Frontend charts

**Statement**: The frontend uses Recharts 2 for all five chart types.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/src/components/charts/`.

**Priority**: Must

##### REQ-TECH-005: Frontend server state

**Statement**: The frontend uses TanStack Query 5 for server state
management, including caching, retries, and invalidation.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/src/hooks/` and `frontend/src/main.tsx`.

**Priority**: Must

##### REQ-TECH-006: Frontend forms and validation

**Statement**: The frontend uses React Hook Form 7 with Zod 3 for
form state and validation.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/src/components/forms/` and
`frontend/src/utils/validation.ts`.

**Priority**: Must

##### REQ-TECH-007: Frontend HTTP client

**Statement**: The frontend uses Axios 1 with request and response
interceptors for auth token attachment and error normalization.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/src/api/client.ts`.

**Priority**: Must

##### REQ-TECH-008: Frontend date utilities

**Statement**: The frontend uses date-fns 3 for date manipulation.

**Source**: `Chapter3_TechStack.md §3.1.1`

**Verification**: Read `frontend/src/utils/date.ts` and
`frontend/package.json`.

**Priority**: Should

##### REQ-TECH-009: Frontend testing tools

**Statement**: The frontend uses Vitest 1 with React Testing Library
14 and MSW 2 for unit, component, and API mocking tests.

**Source**: `Chapter3_TechStack.md §3.1.2`

**Verification**: Read `frontend/package.json` and
`frontend/src/test/`.

**Priority**: Must

##### REQ-TECH-010: Frontend linting and formatting

**Statement**: The frontend uses ESLint 8, Prettier 3, and
TypeScript ESLint 7.

**Source**: `Chapter3_TechStack.md §3.1.2`

**Verification**: Read `frontend/.eslintrc.cjs` and
`frontend/.prettierrc`.

**Priority**: Should

#### 7.2 Backend Stack

##### REQ-TECH-020: Backend language and framework

**Statement**: The backend uses Python 3.12 with FastAPI 0.110+.

**Source**: `Chapter3_TechStack.md §3.2.1`

**Verification**: Read `backend/pyproject.toml`.

**Priority**: Must

##### REQ-TECH-021: Backend ORM and migrations

**Statement**: The backend uses SQLAlchemy 2.0 and Alembic 1.13+.

**Source**: `Chapter3_TechStack.md §3.2.1`

**Verification**: Read `backend/pyproject.toml` and `backend/alembic/`.

**Priority**: Must

##### REQ-TECH-022: Backend validation

**Statement**: The backend uses Pydantic 2 for request and response
validation, including Decimal support.

**Source**: `Chapter3_TechStack.md §3.2.1`

**Verification**: Read `backend/app/schemas/`.

**Priority**: Must

##### REQ-TECH-023: Backend JWT and password libraries

**Statement**: The backend uses python-jose 3.3+ for JWT and
passlib[bcrypt] 1.7+ for password hashing.

**Source**: `Chapter3_TechStack.md §3.2.1`

**Verification**: Read `backend/pyproject.toml` and
`backend/app/auth/`.

**Priority**: Must

##### REQ-TECH-024: Backend server

**Statement**: The backend uses uvicorn 0.29+ as the ASGI server.

**Source**: `Chapter3_TechStack.md §3.2.1`

**Verification**: Read `backend/Dockerfile` and `backend/pyproject.toml`.

**Priority**: Must

##### REQ-TECH-025: Backend dependency management

**Statement**: The backend uses uv for dependency management with a
committed `uv.lock`.

**Source**: `Chapter3_TechStack.md §3.2.1`

**Verification**: Confirm `backend/uv.lock` exists; run `uv sync`.

**Priority**: Must

##### REQ-TECH-026: Backend HTTP client

**Statement**: The backend uses httpx 0.27+ for testing and for the
MCP server's API calls.

**Source**: `Chapter3_TechStack.md §3.2.1`

**Verification**: Read `backend/pyproject.toml` and
`mcp-server/pyproject.toml`.

**Priority**: Must

##### REQ-TECH-027: Backend testing tools

**Statement**: The backend uses pytest 8, pytest-cov 5, and
pytest-asyncio 0.23+.

**Source**: `Chapter3_TechStack.md §3.2.2`

**Verification**: Read `backend/pyproject.toml`.

**Priority**: Must

##### REQ-TECH-028: Backend linting and type checking

**Statement**: The backend uses ruff 0.4+ for linting and formatting,
and mypy 1.10+ for static type checking.

**Source**: `Chapter3_TechStack.md §3.2.2`

**Verification**: Read `backend/pyproject.toml`; run `make lint`.

**Priority**: Should

#### 7.3 Database Strategy

##### REQ-TECH-030: Database per environment

**Statement**: Local development defaults to SQLite, Docker Compose
uses PostgreSQL 16, production uses Render PostgreSQL 16, and fallback
uses SQLite.

**Source**: `Chapter3_TechStack.md §3.3.1`

**Verification**: Read `.env.example`, `docker-compose.yml`, and
`render.yaml`.

**Priority**: Must

##### REQ-TECH-031: Database abstraction

**Statement**: All database access goes through SQLAlchemy. No raw SQL
exists in application code except in migrations.

**Source**: `Chapter3_TechStack.md §3.3.5`

**Verification**: Search for raw SQL in `backend/app/`.

**Priority**: Must

##### REQ-TECH-032: SQLite-specific handling

**Statement**: SQLite uses `PRAGMA foreign_keys = ON` per connection,
`check_same_thread: False`, avoids PostgreSQL-specific functions, and
generates UUIDs in Python.

**Source**: `Chapter3_TechStack.md §3.3.4`

**Verification**: Read `backend/app/database.py` and
`backend/app/models/`.

**Priority**: Must

#### 7.4 Containerization Strategy

##### REQ-TECH-040: Docker base images

**Statement**: The frontend build stage uses `node:20-alpine`, the
backend runtime uses `python:3.12-slim`, and Compose uses
`postgres:16-alpine`.

**Source**: `Chapter3_TechStack.md §3.4.1`

**Verification**: Read `Dockerfile` and `docker-compose.yml`.

**Priority**: Must

##### REQ-TECH-041: Docker Compose services

**Statement**: Docker Compose defines two services: `db` (PostgreSQL)
and `app` (full-stack application on port 8000).

**Source**: `Chapter3_TechStack.md §3.4.2`

**Verification**: Read `docker-compose.yml`.

**Priority**: Must

##### REQ-TECH-042: Single app container

**Statement**: In production, the frontend is built to static files
and served by FastAPI from a single container.

**Source**: `Chapter3_TechStack.md §3.4.2`

**Verification**: Read `Dockerfile`; confirm frontend `dist` is copied
into the backend image.

**Priority**: Must

#### 7.5 CI/CD Strategy

##### REQ-TECH-050: CI/CD provider

**Statement**: GitHub Actions runs three workflows: `ci.yml`,
`e2e.yml`, and `deploy.yml`.

**Source**: `Chapter3_TechStack.md §3.5.1`

**Verification**: Read `.github/workflows/`.

**Priority**: Must

##### REQ-TECH-051: Workflow triggers

**Statement**: `ci.yml` runs on PR and push to main; `e2e.yml` runs
on push to main; `deploy.yml` runs after `e2e.yml` succeeds.

**Source**: `Chapter3_TechStack.md §3.5.1`

**Verification**: Read workflow triggers.

**Priority**: Must

#### 7.6 Deployment Strategy

##### REQ-TECH-060: Deployment platform

**Statement**: The application deploys to Render free tier with a
free PostgreSQL database.

**Source**: `Chapter3_TechStack.md §3.6.1`

**Verification**: Read `render.yaml`; open the live URL.

**Priority**: Must

##### REQ-TECH-061: Render free tier limitations

**Statement**: The project documents Render free tier limitations:
15-minute idle sleep, 30-day PostgreSQL expiry, 512 MB RAM, 0.1 CPU,
no SSH, no persistent disk, 750 hours/month, 5 GB bandwidth/month,
500 build minutes/month.

**Source**: `Chapter3_TechStack.md §3.6.2`

**Verification**: Read `README.md` and `ops/runbook.md`.

**Priority**: Should

##### REQ-TECH-062: Cold start mitigation

**Statement**: UptimeRobot pings the health endpoint every 10 minutes
to reduce cold starts.

**Source**: `Chapter3_TechStack.md §3.6.2`

**Verification**: Confirm UptimeRobot monitor exists; read `README.md`.

**Priority**: Should

#### 7.7 Development Tools

##### REQ-TECH-070: AI coding agent

**Statement**: The project uses pi-agent with qwen3.8-27b running
locally, with plugins added as needed.

**Source**: `Chapter3_TechStack.md §3.7.1`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-TECH-071: AI data policy

**Statement**: All code, prompts, and context stay on the local
machine. No data is sent to cloud LLM providers.

**Source**: `Chapter3_TechStack.md §3.7.1`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

##### REQ-TECH-072: Version control

**Statement**: The project uses Git, GitHub, Conventional Commits, and
feature branches.

**Source**: `Chapter3_TechStack.md §3.7.2`

**Verification**: Inspect git log; read `README.md`.

**Priority**: Should

##### REQ-TECH-073: Code quality tools

**Statement**: The project uses ruff and mypy for Python, ESLint and
Prettier for TypeScript, and the TypeScript compiler for type checking.

**Source**: `Chapter3_TechStack.md §3.7.3`

**Verification**: Read config files; run `make lint`.

**Priority**: Should

##### REQ-TECH-074: Security scanning tools

**Statement**: The project uses gitleaks, semgrep, trivy, pip-audit,
and npm audit. All scans run locally and results are committed to
`security/`.

**Source**: `Chapter3_TechStack.md §3.7.4`

**Verification**: Read `security/`; run `make security`.

**Priority**: Must

##### REQ-TECH-075: Testing tools

**Statement**: The project uses pytest, Vitest, React Testing Library,
MSW, Playwright, and httpx.

**Source**: `Chapter3_TechStack.md §3.7.5`

**Verification**: Read test configs and test files.

**Priority**: Must

##### REQ-TECH-076: Monitoring tools

**Statement**: The project uses Render logs, the health check
endpoint, and UptimeRobot.

**Source**: `Chapter3_TechStack.md §3.7.6`

**Verification**: Read `ops/` documentation.

**Priority**: Should

#### 7.8 Version Pinning

##### REQ-TECH-080: Backend version pinning

**Statement**: Backend dependencies are pinned via `pyproject.toml`
and `uv.lock`.

**Source**: `Chapter3_TechStack.md §3.9`

**Verification**: Confirm `backend/uv.lock` is committed.

**Priority**: Must

##### REQ-TECH-081: Frontend version pinning

**Statement**: Frontend dependencies are pinned via `package.json`
and `package-lock.json`.

**Source**: `Chapter3_TechStack.md §3.9`

**Verification**: Confirm `frontend/package-lock.json` is committed.

**Priority**: Must

##### REQ-TECH-082: Docker image pinning

**Statement**: Docker base images are pinned to specific tags; no
`latest` tags in production Dockerfiles.

**Source**: `Chapter3_TechStack.md §3.9`

**Verification**: Read `Dockerfile` and `docker-compose.yml`.

**Priority**: Must

##### REQ-TECH-083: GitHub Actions pinning

**Statement**: GitHub Actions are pinned to major versions (e.g.,
`actions/checkout@v4`).

**Source**: `Chapter3_TechStack.md §3.9`

**Verification**: Read `.github/workflows/`.

**Priority**: Should

#### 7.9 Environment Variables

##### REQ-TECH-090: Environment variable list

**Statement**: All configuration is via environment variables listed
in `.env.example`, covering DATABASE_URL, JWT settings, CORS, ENVIRONMENT,
APP_VERSION, DB_CONNECT_TIMEOUT, VITE_API_BASE_URL, MCP_API_BASE_URL,
and MCP_JWT_SECRET.

**Source**: `Chapter3_TechStack.md §3.10`

**Verification**: Read `.env.example`.

**Priority**: Must

##### REQ-TECH-091: No real secrets in .env.example

**Statement**: `.env.example` contains only placeholders and defaults;
no real secrets.

**Source**: `Chapter3_TechStack.md §3.10`

**Verification**: Read `.env.example`; run gitleaks.

**Priority**: Must

---

### 8. System Architecture Requirements

**Source**: `requirements/Chapter4_SystemArchitecture.md`

#### 8.1 Architecture Overview

##### REQ-ARCH-001: Three-tier architecture

**Statement**: The system follows a three-tier architecture:
presentation (React SPA), application (FastAPI), and data
(PostgreSQL/SQLite), plus an agent layer alongside the application tier.

**Source**: `Chapter4_SystemArchitecture.md §4.1`

**Verification**: Read `docs/architecture.md`; inspect directory
structure.

**Priority**: Must

##### REQ-ARCH-002: Agent layer shares API

**Statement**: The agent layer uses the same API and JWT authentication
as the frontend. No special backend endpoints exist for agents.

**Source**: `Chapter4_SystemArchitecture.md §4.1.1`

**Verification**: Read `mcp-server/`; confirm only standard endpoints
are called.

**Priority**: Must

##### REQ-ARCH-003: Development vs production architecture

**Statement**: Development runs Vite dev server, uvicorn with reload,
and PostgreSQL in Docker. Production runs a single Docker container
serving the built frontend and API, plus a managed PostgreSQL.

**Source**: `Chapter4_SystemArchitecture.md §4.1.2`

**Verification**: Read `docker-compose.yml` and `Dockerfile`.

**Priority**: Must

#### 8.2 Frontend Architecture

##### REQ-ARCH-010: Frontend layered structure

**Statement**: The frontend is organized into entry, pages,
components, hooks, context, API, utils, and types layers.

**Source**: `Chapter4_SystemArchitecture.md §4.2.1`

**Verification**: Read `frontend/src/` directory tree.

**Priority**: Must

##### REQ-ARCH-011: Frontend data flow

**Statement**: The frontend data flow is: user action → page
component → hook → React Query → API module → axios → backend.

**Source**: `Chapter4_SystemArchitecture.md §4.2.2`

**Verification**: Trace a request through the code.

**Priority**: Must

##### REQ-ARCH-012: State ownership

**Statement**: Auth state lives in AuthContext, selected month in
MonthContext, server data in React Query cache, form state in React
Hook Form, and UI state in component-local state.

**Source**: `Chapter4_SystemArchitecture.md §4.2.3`

**Verification**: Read context files and hooks.

**Priority**: Must

##### REQ-ARCH-013: Provider nesting order

**Statement**: Providers are nested in this order: QueryClientProvider
→ BrowserRouter → AuthProvider → MonthProvider → ToastProvider.

**Source**: `Chapter4_SystemArchitecture.md §4.2.4`

**Verification**: Read `frontend/src/main.tsx`.

**Priority**: Must

#### 8.3 Backend Architecture

##### REQ-ARCH-020: Backend layered structure

**Statement**: The backend is organized into entry, config, database,
routers, services, models, schemas, auth, audit, and core layers.

**Source**: `Chapter4_SystemArchitecture.md §4.3.1`

**Verification**: Read `backend/app/` directory tree.

**Priority**: Must

##### REQ-ARCH-021: Request lifecycle

**Statement**: A request goes through middleware, router, dependencies
(including get_current_user), service, database, and back through
response schema.

**Source**: `Chapter4_SystemArchitecture.md §4.3.2`

**Verification**: Trace a request through the code.

**Priority**: Must

##### REQ-ARCH-022: Dependency injection

**Statement**: FastAPI dependencies provide `get_db`,
`get_current_user`, `get_settings`, and `get_audit_logger`.

**Source**: `Chapter4_SystemArchitecture.md §4.3.3`

**Verification**: Read `backend/app/auth/dependencies.py` and
`backend/app/database.py`.

**Priority**: Must

##### REQ-ARCH-023: Transaction boundaries

**Statement**: Each request runs in one database session; services
commit at the end; audit log write is part of the same transaction;
read-only endpoints do not commit.

**Source**: `Chapter4_SystemArchitecture.md §4.3.4`

**Verification**: Read service methods; confirm commit placement.

**Priority**: Must

##### REQ-ARCH-024: Error handling

**Statement**: All errors return a consistent shape
`{detail, code, field}` with appropriate HTTP status codes.

**Source**: `Chapter4_SystemArchitecture.md §4.3.5`

**Verification**: Trigger errors; check response shape.

**Priority**: Must

#### 8.4 Data Flow

##### REQ-ARCH-030: Login flow

**Statement**: Login flow: user enters credentials → frontend POST
/auth/login → backend verifies bcrypt → signs JWT → returns token and
user → frontend stores token and redirects.

**Source**: `Chapter4_SystemArchitecture.md §4.4.1`

**Verification**: Trace the flow in code; run integration test.

**Priority**: Must

##### REQ-ARCH-031: Create expense flow

**Statement**: Create expense flow: frontend POST /expenses with
Bearer JWT → backend verifies JWT, validates body, checks category →
inserts expense and audit log in one transaction → returns 201 →
frontend invalidates caches.

**Source**: `Chapter4_SystemArchitecture.md §4.4.2`

**Verification**: Trace the flow; run integration test.

**Priority**: Must

##### REQ-ARCH-032: Dashboard load flow

**Statement**: Dashboard load issues six parallel requests (summary,
by-category, trend, cumulative, heatmap, recent), aggregates in
Python where needed, and renders five charts.

**Source**: `Chapter4_SystemArchitecture.md §4.4.3`

**Verification**: Read `DashboardPage.tsx` and `useDashboard.ts`.

**Priority**: Must

##### REQ-ARCH-033: Database fallback flow

**Statement**: On startup, the app tries PostgreSQL with a 5-second
timeout; on failure, it logs a warning, creates SQLite tables, seeds
categories, and reports `fallback_active: true` in health.

**Source**: `Chapter4_SystemArchitecture.md §4.4.4`

**Verification**: Follow `ops/diagnosis.md`.

**Priority**: Must

#### 8.5 Authentication Flow

##### REQ-ARCH-040: JWT structure

**Statement**: JWT contains sub, iss, aud, exp, iat, and type claims.

**Source**: `Chapter4_SystemArchitecture.md §4.5.1`

**Verification**: Decode a token.

**Priority**: Must

##### REQ-ARCH-041: Token validation steps

**Statement**: Every protected request validates Bearer header,
decodes JWT with fixed HS256, verifies signature, exp, aud, iss,
extracts sub, loads user, checks is_active.

**Source**: `Chapter4_SystemArchitecture.md §4.5.2`

**Verification**: Read `backend/app/auth/jwt.py` and
`dependencies.py`.

**Priority**: Must

##### REQ-ARCH-042: Token storage

**Statement**: The token is stored in localStorage under key `token`,
sent as `Authorization: Bearer <token>`, expires in 24 hours, with no
refresh token in MVP.

**Source**: `Chapter4_SystemArchitecture.md §4.5.3`

**Verification**: Read `AuthContext.tsx` and `client.ts`.

**Priority**: Must

#### 8.6 Directory Structure

##### REQ-ARCH-050: Repository root structure

**Statement**: The repository root contains README, product-spec,
AGENTS.md, CLAUDE.md, openapi.yaml, docker-compose.yml, render.yaml,
Makefile, .env.example, .gitignore, LICENSE, Dockerfile, and the
directories `.github/`, `frontend/`, `backend/`, `e2e/`, `docs/`,
`security/`, `ops/`, `agent-capabilities/`, `agent-hooks/`,
`mcp-server/`, `custom-agent/`, and `screenshots/`.

**Source**: `Chapter4_SystemArchitecture.md §4.6.1`

**Verification**: List the repository root.

**Priority**: Must

##### REQ-ARCH-051: Frontend directory structure

**Statement**: The frontend contains `src/` with api, components,
pages, hooks, context, types, utils, test; plus `public/`, config
files, and Dockerfile.

**Source**: `Chapter4_SystemArchitecture.md §4.6.2`

**Verification**: List `frontend/`.

**Priority**: Must

##### REQ-ARCH-052: Backend directory structure

**Statement**: The backend contains `app/` with main, config,
database, models, schemas, routers, services, auth, audit, core;
plus tests, alembic, config files, and Dockerfile.

**Source**: `Chapter4_SystemArchitecture.md §4.6.3`

**Verification**: List `backend/`.

**Priority**: Must

##### REQ-ARCH-053: Agent layer directory structure

**Statement**: The agent layer contains `agent-capabilities/`,
`agent-hooks/`, `mcp-server/`, `custom-agent/`, and `.agents/` with
symlinks.

**Source**: `Chapter4_SystemArchitecture.md §4.6.4`

**Verification**: List those directories.

**Priority**: Must

##### REQ-ARCH-054: Documentation and artifacts structure

**Statement**: `docs/` contains architecture, api, process,
ai-workflow, design-system, testing-guidelines, agent-extension-pack,
permissions, task-template, and team/. `security/` contains eight
files. `ops/` contains five files.

**Source**: `Chapter4_SystemArchitecture.md §4.6.5`

**Verification**: List each directory.

**Priority**: Must

#### 8.7 Cross-Cutting Concerns

##### REQ-ARCH-060: Logging

**Statement**: Logs are JSON structured, level INFO in production,
include a request ID, never include sensitive data, and cover key
events.

**Source**: `Chapter4_SystemArchitecture.md §4.7.1`

**Verification**: Read `backend/app/core/logging.py` and
`ops/logging.md`.

**Priority**: Must

##### REQ-ARCH-061: Configuration priority

**Statement**: Configuration priority is environment variables >
`.env` file > defaults in `config.py`.

**Source**: `Chapter4_SystemArchitecture.md §4.7.2`

**Verification**: Read `backend/app/config.py`.

**Priority**: Must

##### REQ-ARCH-062: Error handling layers

**Statement**: Routers raise AppError or HTTPException; services
raise AppError; database errors become 503; axios normalizes errors;
UI shows field errors, toasts, or redirects.

**Source**: `Chapter4_SystemArchitecture.md §4.7.3`

**Verification**: Read `backend/app/core/errors.py` and
`frontend/src/api/client.ts`.

**Priority**: Must

##### REQ-ARCH-063: Security cross-cutting

**Statement**: Passwords use bcrypt, tokens use HS256 with env secret,
token validation covers signature/exp/aud/iss, all queries filter by
user_id, cross-user access returns 404, secrets are never committed,
and audit logs are written in the same transaction.

**Source**: `Chapter4_SystemArchitecture.md §4.7.4`

**Verification**: Read security docs; run isolation tests.

**Priority**: Must

##### REQ-ARCH-064: Testing cross-cutting

**Statement**: Backend unit, backend integration, frontend unit,
frontend component, and E2E tests exist in their respective
locations.

**Source**: `Chapter4_SystemArchitecture.md §4.7.5`

**Verification**: List test directories.

**Priority**: Must

#### 8.8 Architectural Decisions

##### REQ-ARCH-070: Centralized API layer

**Statement**: All backend calls from the frontend go through
`src/api/` as a single integration point.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Inspect frontend code for direct fetch/axios calls.

**Priority**: Must

##### REQ-ARCH-071: Backend serves frontend static files

**Statement**: In production, FastAPI serves the built frontend static
files.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `backend/app/main.py` static mounting.

**Priority**: Must

##### REQ-ARCH-072: SQLAlchemy abstraction

**Statement**: All database access goes through SQLAlchemy 2.0,
enabling PostgreSQL and SQLite without code changes.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read models and services.

**Priority**: Must

##### REQ-ARCH-073: Automatic SQLite fallback

**Statement**: The SQLite fallback triggers only on startup, keeping
the design simple and predictable.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `backend/app/database.py`.

**Priority**: Must

##### REQ-ARCH-074: JWT storage choice

**Statement**: JWT is stored in localStorage rather than an HttpOnly
cookie, documented as a trade-off with mitigations.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-ARCH-075: No refresh token

**Statement**: The MVP uses a 24-hour access token with no refresh
token, documented as a trade-off.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `backend/app/auth/jwt.py`.

**Priority**: Must

##### REQ-ARCH-076: Single production container

**Statement**: The frontend is built into the backend image as a
single container to simplify Render configuration.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `Dockerfile`.

**Priority**: Must

##### REQ-ARCH-077: Agent layer uses same API

**Statement**: The agent layer calls the same backend API with the
same JWT, with no special endpoints.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `mcp-server/tools/`.

**Priority**: Must

##### REQ-ARCH-078: Audit in same transaction

**Statement**: Audit log writes happen in the service layer within
the same transaction as the business operation.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `backend/app/services/` and
`backend/app/audit/logger.py`.

**Priority**: Must

##### REQ-ARCH-079: Month selector in context

**Statement**: The selected month lives in MonthContext, enabling
global chart synchronization.

**Source**: `Chapter4_SystemArchitecture.md §4.8`

**Verification**: Read `MonthContext.tsx` and `DashboardPage.tsx`.

**Priority**: Must

#### 8.9 Constraints and Assumptions

##### REQ-ARCH-080: Platform constraints

**Statement**: The project operates within Render free tier
constraints: 512 MB RAM, 0.1 CPU, 15-minute idle sleep, 1 GB database
storage, 30-day database expiry.

**Source**: `Chapter4_SystemArchitecture.md §4.9.1`

**Verification**: Read `ops/runbook.md` and `render.yaml`.

**Priority**: Must

##### REQ-ARCH-081: Project assumptions

**Statement**: The project assumes stable internet, modern browsers,
low traffic (demo and peer review), small data volume per user, and
that the agent layer runs on the developer's local machine.

**Source**: `Chapter4_SystemArchitecture.md §4.9.2`

**Verification**: Read `docs/architecture.md`.

**Priority**: Should

##### REQ-ARCH-082: Known limitations

**Statement**: Known limitations are documented: cold start on Render,
PostgreSQL 30-day expiry, no refresh token, no rate limiting,
localStorage JWT, SQLite fallback data loss, and no connection pooling
for SQLite.

**Source**: `Chapter4_SystemArchitecture.md §4.9.3`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

---

## Part 4: Data and API Requirements

### 9. Database Design Requirements

**Source**: `requirements/Chapter5_DatabaseDesign.md`

#### 9.1 Overview

##### REQ-DB-001: Five entities

**Statement**: The database stores exactly five entities: users,
categories, expenses, budgets, and audit_logs.

**Source**: `Chapter5_DatabaseDesign.md §5.1`

**Verification**: Read `backend/app/models/`.

**Priority**: Must

##### REQ-DB-002: UUID primary keys

**Statement**: All tables use UUID primary keys generated in Python,
not by the database.

**Source**: `Chapter5_DatabaseDesign.md §5.1`

**Verification**: Read model definitions; confirm `default=uuid4`.

**Priority**: Must

##### REQ-DB-003: Timestamps

**Statement**: Timestamps use `TIMESTAMPTZ` on PostgreSQL and ISO text
on SQLite. SQLAlchemy handles the conversion.

**Source**: `Chapter5_DatabaseDesign.md §5.1`

**Verification**: Read model definitions.

**Priority**: Must

#### 9.2 Table: users

##### REQ-DB-010: users table definition

**Statement**: The users table has id (UUID, PK), email (VARCHAR(255),
UNIQUE, NOT NULL, INDEX), username (VARCHAR(50), UNIQUE, NOT NULL),
hashed_password (VARCHAR(255), NOT NULL), is_active (BOOLEAN, NOT NULL,
DEFAULT TRUE), created_at (TIMESTAMPTZ), updated_at (TIMESTAMPTZ).

**Source**: `Chapter5_DatabaseDesign.md §5.3.1`

**Verification**: Read `backend/app/models/user.py`; inspect migration
`001_initial_schema.py`.

**Priority**: Must

##### REQ-DB-011: users business rules

**Statement**: Email is unique and case-insensitive; username is
unique and case-sensitive; password is never stored in plain text;
`is_active = false` prevents login but preserves data; deleting a
user cascades to categories, expenses, and budgets; audit logs are
not cascaded.

**Source**: `Chapter5_DatabaseDesign.md §5.3.4`

**Verification**: Read model and service code; run integration tests.

**Priority**: Must

#### 9.3 Table: categories

##### REQ-DB-020: categories table definition

**Statement**: The categories table has id (UUID, PK), user_id
(UUID, FK users.id, NULLABLE, INDEX), name (VARCHAR(100), NOT NULL),
color (VARCHAR(7), NOT NULL), icon (VARCHAR(50), NULLABLE), is_system
(BOOLEAN, NOT NULL, DEFAULT FALSE), created_at (TIMESTAMPTZ).

**Source**: `Chapter5_DatabaseDesign.md §5.4.1`

**Verification**: Read `backend/app/models/category.py`.

**Priority**: Must

##### REQ-DB-021: categories constraints

**Statement**: The categories table has two CHECK constraints:
`color ~ '^#[0-9A-Fa-f]{6}$'` and system consistency
`(is_system = TRUE AND user_id IS NULL) OR (is_system = FALSE AND user_id IS NOT NULL)`.

**Source**: `Chapter5_DatabaseDesign.md §5.4.2`

**Verification**: Read model `__table_args__`.

**Priority**: Must

##### REQ-DB-022: categories uniqueness

**Statement**: A partial unique index on `(user_id, name) WHERE
user_id IS NOT NULL` enforces uniqueness within a user's custom
categories. System category uniqueness is enforced by seeding logic.

**Source**: `Chapter5_DatabaseDesign.md §5.4.5`

**Verification**: Read migration; inspect index.

**Priority**: Must

##### REQ-DB-023: categories business rules

**Statement**: System categories have `user_id IS NULL` and
`is_system = TRUE`; custom categories have `user_id = current_user.id`
and `is_system = FALSE`; users cannot create, update, or delete system
categories; color must be valid HEX; categories with expenses cannot
be deleted (returns 409).

**Source**: `Chapter5_DatabaseDesign.md §5.4.4`

**Verification**: Read service code; run category integration tests.

**Priority**: Must

#### 9.4 Table: expenses

##### REQ-DB-030: expenses table definition

**Statement**: The expenses table has id (UUID, PK), user_id (UUID,
FK users.id, NOT NULL, INDEX), category_id (UUID, FK categories.id,
NOT NULL, INDEX), amount (NUMERIC(12,2), NOT NULL, CHECK > 0),
currency (VARCHAR(3), NOT NULL, DEFAULT 'USD'), date (DATE, NOT NULL,
INDEX), note (TEXT, NULLABLE), created_at, updated_at (TIMESTAMPTZ).

**Source**: `Chapter5_DatabaseDesign.md §5.5.1`

**Verification**: Read `backend/app/models/expense.py`.

**Priority**: Must

##### REQ-DB-031: expenses constraints

**Statement**: The expenses table has two CHECK constraints:
`amount > 0` and `currency = 'USD'`.

**Source**: `Chapter5_DatabaseDesign.md §5.5.2`

**Verification**: Read model `__table_args__`.

**Priority**: Must

##### REQ-DB-032: expenses foreign keys

**Statement**: `user_id` references `users.id` with CASCADE;
`category_id` references `categories.id` with RESTRICT.

**Source**: `Chapter5_DatabaseDesign.md §5.5.2`

**Verification**: Read model `ForeignKey` definitions.

**Priority**: Must

##### REQ-DB-033: expenses indexes

**Statement**: The expenses table has indexes on `user_id`,
`(user_id, date DESC)`, `(user_id, category_id)`, and `category_id`.

**Source**: `Chapter5_DatabaseDesign.md §5.5.3`

**Verification**: Read migration.

**Priority**: Must

##### REQ-DB-034: expenses business rules

**Statement**: Amount must be positive with at most 2 decimal places,
maximum 9,999,999,999.99; category must belong to the same user or be
a system category; date is stored without timezone; currency is fixed
to USD; note is optional with max 500 characters; deleting a category
with expenses is restricted.

**Source**: `Chapter5_DatabaseDesign.md §5.5.4`

**Verification**: Run expense integration tests.

**Priority**: Must

#### 9.5 Table: budgets

##### REQ-DB-040: budgets table definition

**Statement**: The budgets table has id (UUID, PK), user_id (UUID,
FK users.id, NOT NULL), year_month (CHAR(7), NOT NULL), amount
(NUMERIC(12,2), NOT NULL, CHECK > 0), created_at, updated_at
(TIMESTAMPTZ).

**Source**: `Chapter5_DatabaseDesign.md §5.6.1`

**Verification**: Read `backend/app/models/budget.py`.

**Priority**: Must

##### REQ-DB-041: budgets constraints

**Statement**: The budgets table has a UNIQUE constraint on
`(user_id, year_month)`, CHECK `amount > 0`, and CHECK `year_month
~ '^[0-9]{4}-[0-9]{2}$'`.

**Source**: `Chapter5_DatabaseDesign.md §5.6.2`

**Verification**: Read model `__table_args__`.

**Priority**: Must

##### REQ-DB-042: budgets business rules

**Statement**: One budget per user per month; setting a budget for an
existing month performs an upsert; year_month format is strictly
YYYY-MM; amount must be positive; deleting a budget does not affect
expenses.

**Source**: `Chapter5_DatabaseDesign.md §5.6.4`

**Verification**: Run budget integration tests.

**Priority**: Must

#### 9.6 Table: audit_logs

##### REQ-DB-050: audit_logs table definition

**Statement**: The audit_logs table has id (UUID, PK), user_id (UUID,
FK users.id, NOT NULL, INDEX), action (VARCHAR(10), NOT NULL),
entity_type (VARCHAR(20), NOT NULL), entity_id (UUID, NOT NULL),
old_value (JSONB, NULLABLE), new_value (JSONB, NULLABLE), ip_address
(VARCHAR(45), NULLABLE), created_at (TIMESTAMPTZ).

**Source**: `Chapter5_DatabaseDesign.md §5.7.1`

**Verification**: Read `backend/app/models/audit_log.py`.

**Priority**: Must

##### REQ-DB-051: audit_logs constraints

**Statement**: The audit_logs table has CHECK `action IN ('CREATE',
'UPDATE', 'DELETE')` and CHECK `entity_type IN ('expense', 'budget')`.

**Source**: `Chapter5_DatabaseDesign.md §5.7.2`

**Verification**: Read model `__table_args__`.

**Priority**: Must

##### REQ-DB-052: audit_logs indexes

**Statement**: The audit_logs table has indexes on
`(user_id, created_at DESC)`, `(entity_type, entity_id)`, and
`action`.

**Source**: `Chapter5_DatabaseDesign.md §5.7.3`

**Verification**: Read migration.

**Priority**: Must

##### REQ-DB-053: audit_logs business rules

**Statement**: Written in the same transaction as the business
operation; if audit write fails, the business operation is rolled
back; not exposed via API; preserved even if the user is deleted;
`old_value` is NULL for CREATE; `new_value` is NULL for DELETE; both
are populated for UPDATE.

**Source**: `Chapter5_DatabaseDesign.md §5.7.4`

**Verification**: Read `backend/app/audit/logger.py` and service
code; run audit tests.

**Priority**: Must

##### REQ-DB-054: audit_logs JSONB handling

**Statement**: PostgreSQL uses JSONB; SQLite uses JSON (stored as
TEXT). SQLAlchemy handles the variant.

**Source**: `Chapter5_DatabaseDesign.md §5.7.2`

**Verification**: Read model definition.

**Priority**: Must

#### 9.7 Indexes and Constraints Summary

##### REQ-DB-060: all indexes

**Statement**: All 14 indexes across the five tables are defined as
listed in the summary table.

**Source**: `Chapter5_DatabaseDesign.md §5.8.1`

**Verification**: Inspect migration `001_initial_schema.py`.

**Priority**: Must

##### REQ-DB-061: all check constraints

**Statement**: All eight CHECK constraints across the five tables are
defined as listed.

**Source**: `Chapter5_DatabaseDesign.md §5.8.2`

**Verification**: Inspect models and migration.

**Priority**: Must

##### REQ-DB-062: all foreign keys

**Statement**: All five foreign key relationships are defined with
the specified ON DELETE behavior (CASCADE for user_id, RESTRICT for
category_id, no cascade for audit_logs.user_id).

**Source**: `Chapter5_DatabaseDesign.md §5.8.3`

**Verification**: Inspect models.

**Priority**: Must

##### REQ-DB-063: SQLite foreign key pragma

**Statement**: SQLite foreign keys are enforced via
`PRAGMA foreign_keys = ON` set per connection through a SQLAlchemy
engine event.

**Source**: `Chapter5_DatabaseDesign.md §5.8.3`

**Verification**: Read `backend/app/database.py`.

**Priority**: Must

#### 9.8 Seed Data

##### REQ-DB-070: ten system categories

**Statement**: Ten system categories are seeded with fixed names,
colors, and icons: Food & Dining (#EF4444), Groceries (#F97316),
Transportation (#EAB308), Housing & Rent (#22C55E), Utilities
(#14B8A6), Entertainment (#3B82F6), Shopping (#8B5CF6),
Health & Fitness (#EC4899), Travel (#06B6D4), Other (#6B7280).

**Source**: `Chapter5_DatabaseDesign.md §5.9.1`

**Verification**: Query the categories table.

**Priority**: Must

##### REQ-DB-071: idempotent seeding

**Statement**: Seeding is idempotent: re-running does not create
duplicates.

**Source**: `Chapter5_DatabaseDesign.md §5.9.2`

**Verification**: Run seeding twice; confirm count is 10.

**Priority**: Must

##### REQ-DB-072: seeding triggers

**Statement**: Seeding runs via Alembic migration for PostgreSQL, and
after `create_all()` for SQLite fallback, tests, and Docker Compose.

**Source**: `Chapter5_DatabaseDesign.md §5.9.3`

**Verification**: Read migration `002_seed_categories.py` and
`backend/app/database.py`.

**Priority**: Must

#### 9.9 Migration Strategy

##### REQ-DB-080: Alembic setup

**Statement**: Alembic manages schema with `env.py`,
`script.py.mako`, and versioned migrations in `versions/`.

**Source**: `Chapter5_DatabaseDesign.md §5.10.1`

**Verification**: Read `backend/alembic/`.

**Priority**: Must

##### REQ-DB-081: migration files

**Statement**: Migration `001_initial_schema.py` creates all five
tables with indexes and constraints; migration
`002_seed_categories.py` inserts the ten system categories and is
idempotent.

**Source**: `Chapter5_DatabaseDesign.md §5.10.2`

**Verification**: Read migration files.

**Priority**: Must

##### REQ-DB-082: migration execution per environment

**Statement**: Local PostgreSQL runs `alembic upgrade head` manually;
Docker Compose runs it on container start; Render runs it via the
container CMD; SQLite fallback and tests use `create_all()`.

**Source**: `Chapter5_DatabaseDesign.md §5.10.3`

**Verification**: Read `Dockerfile`, `docker-compose.yml`, and test
fixtures.

**Priority**: Must

##### REQ-DB-083: fallback does not use Alembic

**Statement**: Fallback data is temporary; migration history is
unnecessary; `create_all()` is faster and avoids SQLite compatibility
issues.

**Source**: `Chapter5_DatabaseDesign.md §5.10.4`

**Verification**: Read `backend/app/database.py`.

**Priority**: Must

#### 9.10 Amount Precision

##### REQ-DB-090: Decimal everywhere

**Statement**: All amounts use Decimal. Layer mapping: database
NUMERIC(12,2), Python Decimal, Pydantic condecimal, JSON string,
frontend input string, frontend display formatted string, audit log
string.

**Source**: `Chapter5_DatabaseDesign.md §5.11.2`

**Verification**: Read models, schemas, and frontend utils.

**Priority**: Must

##### REQ-DB-091: SQLite Decimal handling

**Statement**: SQLite stores NUMERIC as REAL; SQLAlchemy coerces to
Decimal; aggregation quantizes to 0.01 before comparison.

**Source**: `Chapter5_DatabaseDesign.md §5.11.3`

**Verification**: Read `to_decimal` helper; run Decimal tests.

**Priority**: Must

##### REQ-DB-092: aggregation rules

**Statement**: Sums use `func.sum`; result is cast to Decimal and
quantized to 2 decimal places; comparisons use Decimal, never float.

**Source**: `Chapter5_DatabaseDesign.md §5.11.4`

**Verification**: Read `dashboard_service.py`; run aggregation tests.

**Priority**: Must

#### 9.11 Date and Timezone

##### REQ-DB-100: date rules

**Statement**: Expense date uses DATE with no timezone; created_at
and updated_at use TIMESTAMPTZ in UTC; year_month uses CHAR(7) with
no timezone.

**Source**: `Chapter5_DatabaseDesign.md §5.12.1`

**Verification**: Read models.

**Priority**: Must

##### REQ-DB-101: DATE rationale

**Statement**: DATE avoids timezone ambiguity in month attribution.
The user picks a date; that date is stored; that date belongs to that
month.

**Source**: `Chapter5_DatabaseDesign.md §5.12.2`

**Verification**: Read `docs/architecture.md` and Chapter 5.

**Priority**: Must

##### REQ-DB-102: month range query

**Statement**: `month_range("YYYY-MM")` returns `[start, end)` where
end is the first day of the next month.

**Source**: `Chapter5_DatabaseDesign.md §5.12.3`

**Verification**: Read `month_range` helper; run tests.

**Priority**: Must

##### REQ-DB-103: default date

**Statement**: Frontend defaults the date input to today (browser
local timezone); backend stores the date as received without
re-interpretation.

**Source**: `Chapter5_DatabaseDesign.md §5.12.4`

**Verification**: Read `ExpenseForm.tsx` and `expense_service.py`.

**Priority**: Must

##### REQ-DB-104: timestamp defaults

**Statement**: `created_at` and `updated_at` use `func.now()`
(database time), consistent for audit purposes.

**Source**: `Chapter5_DatabaseDesign.md §5.12.5`

**Verification**: Read models.

**Priority**: Must

#### 9.12 Initialization Flow

##### REQ-DB-110: startup sequence

**Statement**: Startup loads settings, determines DATABASE_URL, and
either uses SQLite directly or attempts PostgreSQL with a 5-second
timeout; on failure, logs WARNING and switches to SQLite with
`create_all()` and seeding; `is_fallback` is stored in app state.

**Source**: `Chapter5_DatabaseDesign.md §5.13.1`

**Verification**: Read `backend/app/database.py` and `main.py`.

**Priority**: Must

##### REQ-DB-111: health check reporting

**Statement**: Health endpoint reports `status`, `database`,
`fallback_active`, and `version` based on the `is_fallback` flag.

**Source**: `Chapter5_DatabaseDesign.md §5.13.2`

**Verification**: Call `/api/v1/health`.

**Priority**: Must

##### REQ-DB-112: SQLite engine configuration

**Statement**: SQLite engine uses `check_same_thread: False`,
`StaticPool` for in-memory tests, and a `PRAGMA foreign_keys=ON`
event listener.

**Source**: `Chapter5_DatabaseDesign.md §5.13.3`

**Verification**: Read `backend/app/database.py`.

**Priority**: Must

##### REQ-DB-113: PostgreSQL engine configuration

**Statement**: PostgreSQL engine uses `pool_pre_ping=True`,
`pool_recycle=300`, `pool_size=5`, `max_overflow=10`, and
`connect_timeout=5`.

**Source**: `Chapter5_DatabaseDesign.md §5.13.4`

**Verification**: Read `backend/app/database.py`.

**Priority**: Must

#### 9.13 Data Volume and Backup

##### REQ-DB-120: data volume assumptions

**Statement**: Users < 100, categories per user = 10 system + < 20
custom, expenses per user per month < 200, expenses per user total
< 2000, budgets per user = 1 per month, audit logs per user ~ 3x
expense count.

**Source**: `Chapter5_DatabaseDesign.md §5.14`

**Verification**: Read `docs/architecture.md`.

**Priority**: Should

##### REQ-DB-121: backup scope

**Statement**: No automated backups in MVP. Manual export commands
documented for PostgreSQL (`pg_dump`) and SQLite (`sqlite3 .dump`).

**Source**: `Chapter5_DatabaseDesign.md §5.15`

**Verification**: Read `ops/runbook.md`.

**Priority**: Should

#### 9.14 Database Design Decisions

##### REQ-DB-130: primary key choice

**Statement**: UUID primary keys generated in Python for portability
across PostgreSQL and SQLite.

**Source**: `Chapter5_DatabaseDesign.md §5.16`

**Verification**: Read models.

**Priority**: Must

##### REQ-DB-131: amount type choice

**Statement**: NUMERIC(12,2) for exact decimal representation.

**Source**: `Chapter5_DatabaseDesign.md §5.16`

**Verification**: Read models.

**Priority**: Must

##### REQ-DB-132: date type choice

**Statement**: DATE avoids timezone ambiguity for month attribution.

**Source**: `Chapter5_DatabaseDesign.md §5.16`

**Verification**: Read models.

**Priority**: Must

##### REQ-DB-133: budget key choice

**Statement**: (user_id, year_month) ensures one budget per user per
month.

**Source**: `Chapter5_DatabaseDesign.md §5.16`

**Verification**: Read models.

**Priority**: Must

##### REQ-DB-134: audit entity_id choice

**Statement**: UUID without FK, supporting multiple entity types and
surviving deletion.

**Source**: `Chapter5_DatabaseDesign.md §5.16`

**Verification**: Read model.

**Priority**: Must

##### REQ-DB-135: fallback choice

**Statement**: SQLite on startup only; no runtime switching.

**Source**: `Chapter5_DatabaseDesign.md §5.16`

**Verification**: Read `database.py`.

**Priority**: Must

---

### 10. Backend Design Requirements

**Source**: `requirements/Chapter6_BackendDesign.md`

#### 10.1 Directory Structure and Layering

##### REQ-BE-001: backend directory structure

**Statement**: The backend contains `app/` with main, config,
database, models/, schemas/, routers/, services/, auth/, audit/,
core/; plus tests/unit/, tests/integration/, alembic/, pyproject.toml,
uv.lock, and Dockerfile.

**Source**: `Chapter6_BackendDesign.md §6.1.1`

**Verification**: List `backend/`.

**Priority**: Must

##### REQ-BE-002: layer responsibilities

**Statement**: Each layer has defined responsibilities: entry
(orchestration), config (settings), database (engine), routers
(parsing), services (business), models (ORM), schemas (validation),
auth (JWT/password), audit (writes), core (errors/logging).

**Source**: `Chapter6_BackendDesign.md §6.1.2`

**Verification**: Read the code in each directory.

**Priority**: Must

##### REQ-BE-003: dependency direction

**Statement**: Dependencies point inward: main → routers → services →
models. Models never import services; services never import routers.

**Source**: `Chapter6_BackendDesign.md §6.1.3`

**Verification**: Search for cross-layer imports.

**Priority**: Must

#### 10.2 Configuration

##### REQ-BE-010: Settings class

**Statement**: A Pydantic Settings class loads environment variables
for DATABASE_URL, DB_CONNECT_TIMEOUT, JWT_SECRET, JWT_ALGORITHM,
JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ISSUER, JWT_AUDIENCE,
CORS_ORIGINS, ENVIRONMENT, APP_VERSION, LOG_LEVEL.

**Source**: `Chapter6_BackendDesign.md §6.2.1`

**Verification**: Read `backend/app/config.py`.

**Priority**: Must

##### REQ-BE-011: settings caching

**Statement**: Settings are cached via `@lru_cache`.

**Source**: `Chapter6_BackendDesign.md §6.2.1`

**Verification**: Read `config.py`.

**Priority**: Should

##### REQ-BE-012: production validation

**Statement**: In production, the app refuses to start if
`JWT_SECRET` is the default value or empty.

**Source**: `Chapter6_BackendDesign.md §6.2.3`

**Verification**: Read `config.py`; try starting with default secret.

**Priority**: Must

#### 10.3 JWT Authentication

##### REQ-BE-020: token creation

**Statement**: `create_access_token` creates a JWT with sub, iss,
aud, iat, exp, type claims, signed with HS256.

**Source**: `Chapter6_BackendDesign.md §6.3.1`

**Verification**: Read `backend/app/auth/jwt.py`.

**Priority**: Must

##### REQ-BE-021: token validation

**Statement**: `decode_access_token` validates signature, exp, aud,
iss with fixed algorithm, and checks `type == "access"`.

**Source**: `Chapter6_BackendDesign.md §6.3.2`

**Verification**: Read `jwt.py`; run JWT tests.

**Priority**: Must

##### REQ-BE-022: algorithm fixed

**Statement**: `algorithms=[settings.JWT_ALGORITHM]` is passed to
`jwt.decode`, never taken from the token header. `alg=none` is
rejected.

**Source**: `Chapter6_BackendDesign.md §6.3.3`

**Verification**: Read `jwt.py`; run `test_decode_wrong_algorithm`.

**Priority**: Must

##### REQ-BE-023: no refresh token

**Statement**: The MVP uses a 24-hour access token with no refresh
token; documented as a known limitation.

**Source**: `Chapter6_BackendDesign.md §6.3.5`

**Verification**: Read `jwt.py`; read security notes.

**Priority**: Must

#### 10.4 Password Hashing

##### REQ-BE-030: bcrypt with rounds 12

**Statement**: Passwords are hashed with bcrypt using
`bcrypt__rounds=12`.

**Source**: `Chapter6_BackendDesign.md §6.4.1`

**Verification**: Read `backend/app/auth/password.py`.

**Priority**: Must

##### REQ-BE-031: password validation

**Statement**: Validation is at the Pydantic schema level: min 8
characters, max 72 characters.

**Source**: `Chapter6_BackendDesign.md §6.4.3`

**Verification**: Read `backend/app/schemas/auth.py`.

**Priority**: Must

##### REQ-BE-032: timing attack mitigation

**Statement**: `authenticate_user` runs a dummy bcrypt verification
when the user does not exist, equalizing response time.

**Source**: `Chapter6_BackendDesign.md §6.4.4`

**Verification**: Read `auth_service.py`.

**Priority**: Must

#### 10.5 Dependency Injection

##### REQ-BE-040: get_db

**Statement**: `get_db` provides a SQLAlchemy session per request and
closes it in a `finally` block.

**Source**: `Chapter6_BackendDesign.md §6.5.1`

**Verification**: Read `database.py`.

**Priority**: Must

##### REQ-BE-041: get_current_user

**Statement**: `get_current_user` extracts the Bearer token, decodes
the JWT, loads the user, and checks `is_active`.

**Source**: `Chapter6_BackendDesign.md §6.5.2`

**Verification**: Read `dependencies.py`.

**Priority**: Must

##### REQ-BE-042: get_client_ip

**Statement**: `get_client_ip` reads `X-Forwarded-For` first, then
`request.client.host`.

**Source**: `Chapter6_BackendDesign.md §6.5.4`

**Verification**: Read `dependencies.py`.

**Priority**: Should

#### 10.6 Auth Service

##### REQ-BE-050: register_user

**Statement**: `register_user` normalizes email to lowercase, checks
duplicate email and username, hashes password, and creates the user.

**Source**: `Chapter6_BackendDesign.md §6.6.1`

**Verification**: Read `auth_service.py`; run tests.

**Priority**: Must

##### REQ-BE-051: login_user

**Statement**: `login_user` authenticates, logs failures with a
hashed email, logs success, and returns user plus token.

**Source**: `Chapter6_BackendDesign.md §6.6.2`

**Verification**: Read `auth_service.py`.

**Priority**: Must

#### 10.7 Category Service

##### REQ-BE-060: list_categories

**Statement**: `list_categories` returns system categories plus the
user's custom categories, ordered by `is_system DESC, name`.

**Source**: `Chapter6_BackendDesign.md §6.7.1`

**Verification**: Read `category_service.py`.

**Priority**: Must

##### REQ-BE-061: create_category

**Statement**: `create_category` checks for duplicate names within
the user's scope (case-insensitive) and returns 409 on conflict.

**Source**: `Chapter6_BackendDesign.md §6.7.2`

**Verification**: Read `category_service.py`; run tests.

**Priority**: Must

##### REQ-BE-062: delete_category

**Statement**: `delete_category` only deletes the user's own custom
categories; returns 404 if not found; returns 409 if the category
has expenses.

**Source**: `Chapter6_BackendDesign.md §6.7.3`

**Verification**: Read `category_service.py`; run tests.

**Priority**: Must

##### REQ-BE-063: validate_category_access

**Statement**: `validate_category_access` returns 404 for missing or
not-owned categories, avoiding revealing existence.

**Source**: `Chapter6_BackendDesign.md §6.7.4`

**Verification**: Read `category_service.py`.

**Priority**: Must

#### 10.8 Expense Service

##### REQ-BE-070: create_expense

**Statement**: `create_expense` validates category access, creates
the expense, writes an audit log in the same transaction, commits,
and returns the expense.

**Source**: `Chapter6_BackendDesign.md §6.8.1`

**Verification**: Read `expense_service.py`; run tests.

**Priority**: Must

##### REQ-BE-071: list_expenses

**Statement**: `list_expenses` filters by user_id, applies
year_month and category_id filters, orders by date desc and
created_at desc, and paginates.

**Source**: `Chapter6_BackendDesign.md §6.8.2`

**Verification**: Read `expense_service.py`.

**Priority**: Must

##### REQ-BE-072: get_expense

**Statement**: `get_expense` returns 404 if the expense is missing
or belongs to another user.

**Source**: `Chapter6_BackendDesign.md §6.8.3`

**Verification**: Read `expense_service.py`.

**Priority**: Must

##### REQ-BE-073: update_expense

**Statement**: `update_expense` loads the expense with user_id
filter, validates any new category, applies updates, writes an audit
log with old and new values, and commits.

**Source**: `Chapter6_BackendDesign.md §6.8.4`

**Verification**: Read `expense_service.py`; run tests.

**Priority**: Must

##### REQ-BE-074: delete_expense

**Statement**: `delete_expense` loads the expense with user_id
filter, deletes it, writes an audit log with the old value, and
commits.

**Source**: `Chapter6_BackendDesign.md §6.8.5`

**Verification**: Read `expense_service.py`; run tests.

**Priority**: Must

##### REQ-BE-075: expense serialization helper

**Statement**: `expense_to_dict` returns amount as string,
category_id as string, date as ISO string, and note.

**Source**: `Chapter6_BackendDesign.md §6.8.6`

**Verification**: Read `expense_service.py`.

**Priority**: Must

#### 10.9 Budget Service

##### REQ-BE-080: set_budget upsert

**Statement**: `set_budget` validates year_month, upserts the
budget, writes an audit log (CREATE or UPDATE), and commits.

**Source**: `Chapter6_BackendDesign.md §6.9.1`

**Verification**: Read `budget_service.py`; run tests.

**Priority**: Must

##### REQ-BE-081: get_budget

**Statement**: `get_budget` validates year_month and returns the
budget or None.

**Source**: `Chapter6_BackendDesign.md §6.9.2`

**Verification**: Read `budget_service.py`.

**Priority**: Must

##### REQ-BE-082: delete_budget

**Statement**: `delete_budget` returns 404 if the budget is missing,
otherwise deletes it, writes an audit log, and commits.

**Source**: `Chapter6_BackendDesign.md §6.9.3`

**Verification**: Read `budget_service.py`; run tests.

**Priority**: Must

##### REQ-BE-083: year_month validation

**Statement**: `validate_year_month` checks regex
`^\d{4}-\d{2}$` and month 01-12.

**Source**: `Chapter6_BackendDesign.md §6.9.4`

**Verification**: Read `budget_service.py`; run tests.

**Priority**: Must

#### 10.10 Dashboard Service

##### REQ-BE-090: get_summary

**Statement**: `get_summary` computes total_spent, transaction_count,
budget, remaining, percentage (null if budget is 0), and
is_over_budget.

**Source**: `Chapter6_BackendDesign.md §6.10.1`

**Verification**: Read `dashboard_service.py`; run tests.

**Priority**: Must

##### REQ-BE-091: get_by_category

**Statement**: `get_by_category` groups expenses by category,
computes amount and percentage per category, orders by amount desc.

**Source**: `Chapter6_BackendDesign.md §6.10.2`

**Verification**: Read `dashboard_service.py`; run tests.

**Priority**: Must

##### REQ-BE-092: get_trend

**Statement**: `get_trend` aggregates expenses over the last N
months, includes months with zero expenses, handles year boundaries,
and aggregates in Python to avoid DB-specific date functions.

**Source**: `Chapter6_BackendDesign.md §6.10.3`

**Verification**: Read `dashboard_service.py`; run tests.

**Priority**: Must

##### REQ-BE-093: get_cumulative

**Statement**: `get_cumulative` generates all days in the month,
computes daily and running cumulative amounts, includes days with
zero expenses.

**Source**: `Chapter6_BackendDesign.md §6.10.4`

**Verification**: Read `dashboard_service.py`; run tests.

**Priority**: Must

##### REQ-BE-094: get_heatmap

**Statement**: `get_heatmap` generates a week matrix starting on
Monday, fills missing days with 0, and computes max_amount.

**Source**: `Chapter6_BackendDesign.md §6.10.5`

**Verification**: Read `dashboard_service.py`; run tests.

**Priority**: Must

##### REQ-BE-095: get_recent

**Statement**: `get_recent` returns the user's expenses ordered by
date desc, created_at desc, limited.

**Source**: `Chapter6_BackendDesign.md §6.10.6`

**Verification**: Read `dashboard_service.py`.

**Priority**: Must

##### REQ-BE-096: shared helpers

**Statement**: `month_range`, `add_month`, `subtract_months`, and
`to_decimal` are provided as shared helpers.

**Source**: `Chapter6_BackendDesign.md §6.10.7`

**Verification**: Read `dashboard_service.py`.

**Priority**: Must

#### 10.11 Audit Logging

##### REQ-BE-100: write_audit_log

**Statement**: `write_audit_log` adds an AuditLog to the session
without committing; the caller commits.

**Source**: `Chapter6_BackendDesign.md §6.11.1`

**Verification**: Read `backend/app/audit/logger.py`.

**Priority**: Must

##### REQ-BE-101: audit rules

**Statement**: Same transaction, rollback on failure, no API access,
preserve on user delete, JSON-serializable values, IP address
extracted from request.

**Source**: `Chapter6_BackendDesign.md §6.11.2`

**Verification**: Read service code; run audit tests.

**Priority**: Must

#### 10.12 Error Handling

##### REQ-BE-110: AppError

**Statement**: `AppError` carries code, message, status_code, and
optional field.

**Source**: `Chapter6_BackendDesign.md §6.12.1`

**Verification**: Read `backend/app/core/errors.py`.

**Priority**: Must

##### REQ-BE-111: exception handlers

**Statement**: Handlers exist for AppError, RequestValidationError,
SQLAlchemyError, and generic Exception; all return consistent shape.

**Source**: `Chapter6_BackendDesign.md §6.12.2`

**Verification**: Read `main.py`.

**Priority**: Must

##### REQ-BE-112: error code table

**Statement**: All 18 error codes are defined with HTTP status and
field where applicable.

**Source**: `Chapter6_BackendDesign.md §6.12.3`

**Verification**: Read error code table; search for codes in code.

**Priority**: Must

#### 10.13 Logging

##### REQ-BE-120: JSON logging setup

**Statement**: Logs use a JSON formatter with timestamp, level,
logger, event, extra_fields, and exception when applicable.

**Source**: `Chapter6_BackendDesign.md §6.13.1`

**Verification**: Read `backend/app/core/logging.py`.

**Priority**: Must

##### REQ-BE-121: log events

**Statement**: Events are defined for auth, expense, budget,
category, db fallback, db error, and unhandled error.

**Source**: `Chapter6_BackendDesign.md §6.13.2`

**Verification**: Read service code; inspect log output.

**Priority**: Must

##### REQ-BE-122: never log sensitive data

**Statement**: Passwords, tokens, full bodies, raw emails, and DB
connection strings are never logged.

**Source**: `Chapter6_BackendDesign.md §6.13.3`

**Verification**: Inspect logging calls; run gitleaks.

**Priority**: Must

#### 10.14 SQLite Fallback Logic

##### REQ-BE-130: engine selection

**Statement**: `create_db_engine` uses SQLite directly when
DATABASE_URL starts with sqlite; otherwise tries PostgreSQL with a
5-second timeout and falls back to SQLite on failure, logging
WARNING.

**Source**: `Chapter6_BackendDesign.md §6.14.1`

**Verification**: Read `database.py`; follow `ops/diagnosis.md`.

**Priority**: Must

##### REQ-BE-131: startup initialization

**Statement**: On startup, if fallback is active, create tables and
seed categories; otherwise log primary initialization.

**Source**: `Chapter6_BackendDesign.md §6.14.2`

**Verification**: Read `main.py`.

**Priority**: Must

##### REQ-BE-132: health reporting

**Statement**: Health reports `status`, `database`, `fallback_active`,
`version` based on `is_fallback`.

**Source**: `Chapter6_BackendDesign.md §6.14.3`

**Verification**: Call `/api/v1/health`.

**Priority**: Must

##### REQ-BE-133: fallback rules

**Statement**: Fallback triggers only on startup; timeout 5 seconds;
fallback target `sqlite:///./fallback.db`; requires restart to switch
back; data lost on container restart; all endpoints work normally.

**Source**: `Chapter6_BackendDesign.md §6.14.4`

**Verification**: Follow `ops/diagnosis.md`.

**Priority**: Must

#### 10.15 Main Application

##### REQ-BE-140: app factory

**Statement**: FastAPI app is created with title, version, docs,
redoc, and openapi URLs; CORS middleware; exception handlers; six
routers with /api/v1 prefixes; SPA fallback for static files.

**Source**: `Chapter6_BackendDesign.md §6.15.1`

**Verification**: Read `backend/app/main.py`.

**Priority**: Must

##### REQ-BE-141: router registration order

**Statement**: Routers are registered in order: health, auth,
categories, expenses, budgets, dashboard, static SPA fallback last.

**Source**: `Chapter6_BackendDesign.md §6.15.2`

**Verification**: Read `main.py`.

**Priority**: Must

#### 10.16 Backend Design Decisions

##### REQ-BE-150: framework and ORM

**Statement**: FastAPI and SQLAlchemy 2.0 are chosen for auto
OpenAPI, async support, Pydantic integration, and support for both
PostgreSQL and SQLite.

**Source**: `Chapter6_BackendDesign.md §6.16`

**Verification**: Read `pyproject.toml`.

**Priority**: Must

##### REQ-BE-151: user isolation and 404

**Statement**: User isolation is enforced at the query level; cross-
user access returns 404, not 403, to avoid revealing existence.

**Source**: `Chapter6_BackendDesign.md §6.16`

**Verification**: Read service code; run isolation tests.

**Priority**: Must

##### REQ-BE-152: error format and Decimal

**Statement**: Error format `{detail, code, field}`; Decimal quantized
to 0.01; DATE type without timezone.

**Source**: `Chapter6_BackendDesign.md §6.16`

**Verification**: Read errors and services.

**Priority**: Must

---

### 11. API Contract Requirements

**Source**: `requirements/Chapter7_APIContract(OpenAPI).md`

#### 11.1 Overview

##### REQ-API-001: OpenAPI version

**Statement**: OpenAPI 3.1.0, API version 1.0.0, title "Expense
Tracker & Budget Dashboard API".

**Source**: `Chapter7_APIContract(OpenAPI).md §7.1.1`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

##### REQ-API-002: base URLs

**Statement**: Base URLs: local `http://localhost:8000/api/v1`,
production `https://expense-tracker-dashboard.onrender.com/api/v1`.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.1.2`

**Verification**: Read `openapi.yaml` servers.

**Priority**: Must

##### REQ-API-003: content types

**Statement**: Request, response, and error bodies are
`application/json`; auth uses `Authorization: Bearer <token>`.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.1.3`

**Verification**: Read `openapi.yaml` and `client.ts`.

**Priority**: Must

##### REQ-API-004: authentication scheme

**Statement**: A `bearerAuth` scheme of type http, scheme bearer,
bearerFormat JWT is defined globally; health, register, and login
override with `security: []`.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.1.5`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

#### 11.2 Health Endpoint

##### REQ-API-010: GET /health

**Statement**: `GET /api/v1/health` returns 200 with `status`,
`database`, `fallback_active`, `version`; no auth required.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.2.1`

**Verification**: `curl /api/v1/health`; run health tests.

**Priority**: Must

#### 11.3 Auth Endpoints

##### REQ-API-020: POST /auth/register

**Statement**: `POST /api/v1/auth/register` accepts email, username,
password; returns 201 with user; 409 for duplicates; 422 for
validation errors.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.3.1`

**Verification**: Run auth tests.

**Priority**: Must

##### REQ-API-021: POST /auth/login

**Statement**: `POST /api/v1/auth/login` accepts email and password;
returns 200 with access_token, token_type, user; 401 on invalid
credentials.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.3.2`

**Verification**: Run auth tests.

**Priority**: Must

##### REQ-API-022: GET /auth/me

**Statement**: `GET /api/v1/auth/me` returns 200 with current user;
401 if unauthenticated.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.3.3`

**Verification**: Run auth tests.

**Priority**: Must

#### 11.4 Category Endpoints

##### REQ-API-030: GET /categories

**Statement**: `GET /api/v1/categories` returns system and user
categories.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.4.1`

**Verification**: Run category tests.

**Priority**: Must

##### REQ-API-031: POST /categories

**Statement**: `POST /api/v1/categories` creates a custom category;
returns 201; 409 for duplicate; 422 for invalid color.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.4.2`

**Verification**: Run category tests.

**Priority**: Must

##### REQ-API-032: DELETE /categories/{id}

**Statement**: `DELETE /api/v1/categories/{id}` deletes a custom
category; 204 on success; 404 if not found; 409 if category has
expenses.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.4.3`

**Verification**: Run category tests.

**Priority**: Must

#### 11.5 Expense Endpoints

##### REQ-API-040: GET /expenses

**Statement**: `GET /api/v1/expenses` supports year_month,
category_id, page, page_size; returns paginated list.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.5.1`

**Verification**: Run expense tests.

**Priority**: Must

##### REQ-API-041: POST /expenses

**Statement**: `POST /api/v1/expenses` creates an expense; 201 on
success; 404 if category invalid; 422 for validation errors.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.5.2`

**Verification**: Run expense tests.

**Priority**: Must

##### REQ-API-042: GET /expenses/{id}

**Statement**: `GET /api/v1/expenses/{id}` returns the expense; 404
if not found or not owned.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.5.3`

**Verification**: Run expense tests.

**Priority**: Must

##### REQ-API-043: PUT /expenses/{id}

**Statement**: `PUT /api/v1/expenses/{id}` updates; 200 on success;
404 if not found or not owned; 422 for validation errors.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.5.4`

**Verification**: Run expense tests.

**Priority**: Must

##### REQ-API-044: DELETE /expenses/{id}

**Statement**: `DELETE /api/v1/expenses/{id}` deletes; 204 on
success; 404 if not found or not owned.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.5.5`

**Verification**: Run expense tests.

**Priority**: Must

#### 11.6 Budget Endpoints

##### REQ-API-050: GET /budgets/{year_month}

**Statement**: `GET /api/v1/budgets/{year_month}` returns the budget;
returns 200 with amount "0.00" if no budget exists.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.6.1`

**Verification**: Run budget tests.

**Priority**: Must

##### REQ-API-051: PUT /budgets/{year_month}

**Statement**: `PUT /api/v1/budgets/{year_month}` sets or updates;
returns 200.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.6.2`

**Verification**: Run budget tests.

**Priority**: Must

##### REQ-API-052: DELETE /budgets/{year_month}

**Statement**: `DELETE /api/v1/budgets/{year_month}` deletes; 204 on
success; 404 if no budget.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.6.3`

**Verification**: Run budget tests.

**Priority**: Must

#### 11.7 Dashboard Endpoints

##### REQ-API-060: GET /dashboard/summary

**Statement**: `GET /api/v1/dashboard/summary` returns year_month,
total_spent, budget, remaining, percentage (null if budget = 0),
transaction_count, is_over_budget.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.7.1`

**Verification**: Run dashboard tests.

**Priority**: Must

##### REQ-API-061: GET /dashboard/by-category

**Statement**: `GET /api/v1/dashboard/by-category` returns categories
with category_id, name, color, amount, percentage.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.7.2`

**Verification**: Run dashboard tests.

**Priority**: Must

##### REQ-API-062: GET /dashboard/trend

**Statement**: `GET /api/v1/dashboard/trend` with months (default 6,
max 24) returns months array.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.7.3`

**Verification**: Run dashboard tests.

**Priority**: Must

##### REQ-API-063: GET /dashboard/cumulative

**Statement**: `GET /api/v1/dashboard/cumulative` returns year_month,
budget, days array with date, daily, cumulative.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.7.4`

**Verification**: Run dashboard tests.

**Priority**: Must

##### REQ-API-064: GET /dashboard/heatmap

**Statement**: `GET /api/v1/dashboard/heatmap` with weeks (default
12, max 52) returns max_amount and weeks with week_start and days.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.7.5`

**Verification**: Run dashboard tests.

**Priority**: Must

##### REQ-API-065: GET /dashboard/recent

**Statement**: `GET /api/v1/dashboard/recent` with limit (default 10,
max 50) returns items array of expenses.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.7.6`

**Verification**: Run dashboard tests.

**Priority**: Must

#### 11.8 Error Format

##### REQ-API-070: ErrorResponse schema

**Statement**: Errors return `{detail, code, field?}` with detail
human-readable, code machine-readable, field optional.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.8.1`

**Verification**: Trigger errors; check shape.

**Priority**: Must

##### REQ-API-071: validation error normalization

**Statement**: Validation errors return 422 with the first error
normalized to `{detail, code: "VALIDATION_ERROR", field}`.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.8.2`

**Verification**: Submit invalid data; check response.

**Priority**: Must

##### REQ-API-072: error code reference

**Statement**: All 18 error codes are documented with HTTP status
and condition.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.8.3`

**Verification**: Read `openapi.yaml`; run error tests.

**Priority**: Must

##### REQ-API-073: HTTP status usage

**Statement**: 200 for GET/PUT, 201 for POST, 204 for DELETE, 401
for missing/invalid token, 403 for forbidden, 404 for missing or
not-owned, 409 for conflict, 422 for validation, 500 for unexpected,
503 for database error.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.8.4`

**Verification**: Review endpoint responses.

**Priority**: Must

#### 11.9 Pagination

##### REQ-API-080: pagination parameters

**Statement**: `page` (default 1, min 1) and `page_size` (default
20, min 1, max 100).

**Source**: `Chapter7_APIContract(OpenAPI).md §7.9.1`

**Verification**: Read endpoint definitions.

**Priority**: Must

##### REQ-API-081: pagination response shape

**Statement**: Response contains `items`, `total`, `page`,
`page_size`; `total` is the full count, not page size.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.9.2`

**Verification**: Run expense list tests.

**Priority**: Must

#### 11.10 Formats

##### REQ-API-090: amount format

**Statement**: Amounts are strings matching
`^[0-9]+(\.[0-9]{1,2})?$`, max 2 decimals, min 0.01, max
9,999,999,999.99, always USD.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.10.1`

**Verification**: Read `openapi.yaml`; run tests.

**Priority**: Must

##### REQ-API-091: date format

**Statement**: Dates are ISO 8601 `YYYY-MM-DD` strings with no time
component or timezone.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.10.2`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

##### REQ-API-092: datetime format

**Statement**: Timestamps are ISO 8601 with UTC (`Z` suffix), used
for created_at and updated_at.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.10.3`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

##### REQ-API-093: year-month format

**Statement**: year_month matches `^[0-9]{4}-[0-9]{2}$`, used for
budgets and dashboard filters.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.10.4`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

#### 11.11 Contract Testing

##### REQ-API-100: contract verification

**Statement**: The contract is verified via FastAPI auto-generated
OpenAPI compared to `openapi.yaml`, frontend mocks, integration
tests, and E2E tests.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.13`

**Verification**: Read tests; run comparison.

**Priority**: Must

##### REQ-API-101: schema validation in tests

**Statement**: Integration tests assert response shapes match
OpenAPI schemas.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.13.3`

**Verification**: Read integration tests.

**Priority**: Must

#### 11.12 OpenAPI Design Decisions

##### REQ-API-110: amounts as strings

**Statement**: Amounts are strings to avoid float precision loss.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.14`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

##### REQ-API-111: error format choice

**Statement**: Error format `{detail, code, field}` for consistency.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.14`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

##### REQ-API-112: 404 for cross-user

**Statement**: Cross-user access returns 404, not 403, to avoid
revealing existence.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.14`

**Verification**: Run isolation tests.

**Priority**: Must

##### REQ-API-113: budget missing returns 200

**Statement**: A missing budget returns 200 with amount "0.00",
simplifying the frontend.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.14`

**Verification**: Run budget tests.

**Priority**: Must

##### REQ-API-114: bounded parameters

**Statement**: months 1-24 (default 6), weeks 1-52 (default 12),
limit 1-50 (default 10), page_size max 100.

**Source**: `Chapter7_APIContract(OpenAPI).md §7.14`

**Verification**: Read `openapi.yaml`; run validation tests.

**Priority**: Must

---

## Part 5: Frontend Requirements

### 12. Frontend Design Requirements

**Source**: `requirements/Chapter8_FrontendDesign.md`

#### 12.1 Directory Structure and Layering

##### REQ-FE-001: frontend directory structure

**Statement**: The frontend contains `src/` with api/, components/
(ui/, layout/, charts/, forms/, common/), pages/, hooks/, context/,
types/, utils/, test/; plus `public/`, config files, and Dockerfile.

**Source**: `Chapter8_FrontendDesign.md §8.1.1`

**Verification**: List `frontend/`.

**Priority**: Must

##### REQ-FE-002: layer responsibilities

**Statement**: Entry (bootstrap), pages (route composition),
components (reusable UI), hooks (data fetching), context (global
state), API (HTTP), utils (pure functions), types (TypeScript).

**Source**: `Chapter8_FrontendDesign.md §8.1.2`

**Verification**: Read each directory.

**Priority**: Must

##### REQ-FE-003: import direction

**Statement**: Pages may import anything below them; components may
not import pages; hooks may not import components or pages; API
modules may not import React; utils are pure.

**Source**: `Chapter8_FrontendDesign.md §8.1.3`

**Verification**: Search for violating imports.

**Priority**: Must

#### 12.2 Routing

##### REQ-FE-010: route table

**Statement**: Routes are `/login`, `/register`, `/` (Dashboard),
`/expenses`, `/budgets`, `/categories`, and `*` (NotFound). All
except login/register/notfound require authentication.

**Source**: `Chapter8_FrontendDesign.md §8.2.1`

**Verification**: Read `App.tsx`.

**Priority**: Must

##### REQ-FE-011: router setup with nested routes

**Statement**: Router uses nested routes: PublicOnlyRoute for
login/register; ProtectedRoute wrapping AppShell for the four
authenticated pages.

**Source**: `Chapter8_FrontendDesign.md §8.2.2`

**Verification**: Read `App.tsx`.

**Priority**: Must

##### REQ-FE-012: ProtectedRoute

**Statement**: ProtectedRoute shows a full-page spinner while auth
is loading, redirects unauthenticated users to `/login` with the
original location in state.

**Source**: `Chapter8_FrontendDesign.md §8.2.3`

**Verification**: Read `ProtectedRoute.tsx`.

**Priority**: Must

##### REQ-FE-013: redirect after login

**Statement**: After successful login, redirect to the original
`from` location or `/`.

**Source**: `Chapter8_FrontendDesign.md §8.2.4`

**Verification**: Read `LoginPage.tsx`.

**Priority**: Must

##### REQ-FE-014: public route guard

**Statement**: Logged-in users visiting `/login` or `/register` are
redirected to `/`.

**Source**: `Chapter8_FrontendDesign.md §8.2.5`

**Verification**: Read `PublicOnlyRoute.tsx`.

**Priority**: Must

##### REQ-FE-015: page titles

**Statement**: Each page sets a unique `document.title` following
the pattern `<Page> — Expense Tracker`.

**Source**: `Chapter8_FrontendDesign.md §8.2.6`

**Verification**: Read each page; check browser tab.

**Priority**: Should

#### 12.3 Provider Nesting

##### REQ-FE-020: provider order

**Statement**: Providers are nested QueryClientProvider →
BrowserRouter → AuthProvider → MonthProvider → ToastProvider → App.

**Source**: `Chapter8_FrontendDesign.md §8.3.1`

**Verification**: Read `main.tsx`.

**Priority**: Must

##### REQ-FE-021: provider rationale

**Statement**: Each provider depends only on its ancestors:
QueryClient outermost because Auth uses it; Toast innermost because
any component may trigger it.

**Source**: `Chapter8_FrontendDesign.md §8.3.2`

**Verification**: Read `main.tsx` and context files.

**Priority**: Must

##### REQ-FE-022: provider responsibilities

**Statement**: QueryClientProvider (server cache), BrowserRouter
(routing), AuthProvider (user/token), MonthProvider (yearMonth),
ToastProvider (toast queue).

**Source**: `Chapter8_FrontendDesign.md §8.3.3`

**Verification**: Read each context file.

**Priority**: Must

#### 12.4 State Management

##### REQ-FE-030: state categories

**Statement**: Server state in React Query, auth state in
AuthContext, UI global state in MonthContext, form state in React
Hook Form, URL state in React Router.

**Source**: `Chapter8_FrontendDesign.md §8.4.1`

**Verification**: Read hooks and context files.

**Priority**: Must

##### REQ-FE-031: AuthContext

**Statement**: AuthContext provides `user`, `token`, `isLoading`,
`login`, `register`, `logout`; validates the stored token on mount
via `/auth/me`.

**Source**: `Chapter8_FrontendDesign.md §8.4.2`

**Verification**: Read `AuthContext.tsx`.

**Priority**: Must

##### REQ-FE-032: MonthContext

**Statement**: MonthContext provides `yearMonth`, `setYearMonth`,
`prevMonth`, `nextMonth`, defaulting to the current month.

**Source**: `Chapter8_FrontendDesign.md §8.4.3`

**Verification**: Read `MonthContext.tsx`.

**Priority**: Must

##### REQ-FE-033: ToastContext

**Statement**: ToastContext provides `showToast(message, variant)`;
toasts auto-dismiss after 3 seconds.

**Source**: `Chapter8_FrontendDesign.md §8.4.4`

**Verification**: Read `ToastContext.tsx`.

**Priority**: Must

##### REQ-FE-034: data hooks

**Statement**: Each resource has a dedicated hook wrapping React
Query; mutations invalidate the relevant query keys.

**Source**: `Chapter8_FrontendDesign.md §8.4.5`

**Verification**: Read `hooks/`.

**Priority**: Must

##### REQ-FE-035: hook list

**Statement**: Auth, categories, expenses (list/get/create/update/
delete), budgets (get/set/delete), dashboard (six queries), toast.

**Source**: `Chapter8_FrontendDesign.md §8.4.6`

**Verification**: List `hooks/`.

**Priority**: Must

#### 12.5 API Client

##### REQ-FE-040: axios instance

**Statement**: A single axios instance uses `VITE_API_BASE_URL` with
a 10-second timeout; request interceptor attaches the Bearer token;
response interceptor handles 401 by clearing the token and
redirecting to `/login`.

**Source**: `Chapter8_FrontendDesign.md §8.5.1`

**Verification**: Read `api/client.ts`.

**Priority**: Must

##### REQ-FE-041: error normalization

**Statement**: Errors are normalized to `{status, code, message,
field?}`; network errors map to a distinct code; unknown errors fall
back to a generic message.

**Source**: `Chapter8_FrontendDesign.md §8.5.2`

**Verification**: Read `client.ts`.

**Priority**: Must

##### REQ-FE-042: resource modules

**Statement**: Each resource has its own module with typed functions
mapping one-to-one to OpenAPI endpoints.

**Source**: `Chapter8_FrontendDesign.md §8.5.3`

**Verification**: Read `api/`.

**Priority**: Must

##### REQ-FE-043: API module list

**Statement**: Modules: auth, categories, expenses, budgets,
dashboard, health.

**Source**: `Chapter8_FrontendDesign.md §8.5.4`

**Verification**: List `api/`.

**Priority**: Must

##### REQ-FE-044: centralized API rationale

**Statement**: Centralized API layer for auth header, error
handling, mocking, type safety, and contract alignment.

**Source**: `Chapter8_FrontendDesign.md §8.5.5`

**Verification**: Read `api/client.ts`; search for direct axios/
fetch usage outside `api/`.

**Priority**: Must

#### 12.6 Query Keys

##### REQ-FE-050: query key factory

**Statement**: A `queryKeys` factory defines keys for auth.me,
categories.all, expenses.list/detail, budgets.byMonth, and six
dashboard queries.

**Source**: `Chapter8_FrontendDesign.md §8.6.1`

**Verification**: Read `api/queryKeys.ts`.

**Priority**: Must

##### REQ-FE-051: invalidation strategy

**Statement**: Expense mutations invalidate `["expenses"]` and
`["dashboard"]`; budget mutations invalidate `["budgets"]` and
`["dashboard"]`; category mutations invalidate `["categories"]`.

**Source**: `Chapter8_FrontendDesign.md §8.6.2`

**Verification**: Read hooks.

**Priority**: Must

##### REQ-FE-052: query configuration

**Statement**: staleTime 5 minutes, gcTime 10 minutes, retry 3 for
network and 0 for 4xx, refetchOnWindowFocus false.

**Source**: `Chapter8_FrontendDesign.md §8.6.3`

**Verification**: Read `main.tsx` QueryClient config.

**Priority**: Must

#### 12.7 Page Design

##### REQ-FE-060: LoginPage

**Statement**: Login page has email and password fields, submits via
`useAuth().login`, redirects on success, shows inline error on
failure, and links to `/register`.

**Source**: `Chapter8_FrontendDesign.md §8.7.1`

**Verification**: Read `LoginPage.tsx`; run tests.

**Priority**: Must

##### REQ-FE-061: RegisterPage

**Statement**: Register page has email, username, password, and
confirm password fields; validates on blur; auto-logs in on success;
shows field-level errors; links to `/login`.

**Source**: `Chapter8_FrontendDesign.md §8.7.2`

**Verification**: Read `RegisterPage.tsx`.

**Priority**: Must

##### REQ-FE-062: DashboardPage layout

**Statement**: Dashboard has a header with logo, month picker, and
user menu; four KPI cards; five charts (pie, trend, cumulative,
heatmap, progress); recent transactions list; responsive layout.

**Source**: `Chapter8_FrontendDesign.md §8.7.3`

**Verification**: Read `DashboardPage.tsx`; open the live app.

**Priority**: Must

##### REQ-FE-063: ExpensesPage layout

**Statement**: Expenses page has month and category filters, an add
button, a table with date/category/amount/note/actions columns, and
pagination.

**Source**: `Chapter8_FrontendDesign.md §8.7.4`

**Verification**: Read `ExpensesPage.tsx`.

**Priority**: Must

##### REQ-FE-064: BudgetPage layout

**Statement**: Budget page has a month picker, current budget
display with edit/delete, a set-budget form, and a 12-month budget
history list.

**Source**: `Chapter8_FrontendDesign.md §8.7.5`

**Verification**: Read `BudgetPage.tsx`.

**Priority**: Must

##### REQ-FE-065: CategoriesPage layout

**Statement**: Categories page has a system categories section (no
delete) and a user categories section with delete buttons.

**Source**: `Chapter8_FrontendDesign.md §8.7.6`

**Verification**: Read `CategoriesPage.tsx`.

**Priority**: Must

#### 12.8 Chart Components

##### REQ-FE-070: CategoryPieChart

**Statement**: Pie chart uses Recharts with per-category colors from
the API, tooltip shows name/amount/percentage, merges to top 6 +
Other, and has an empty state.

**Source**: `Chapter8_FrontendDesign.md §8.8.1`

**Verification**: Read `CategoryPieChart.tsx`; run tests.

**Priority**: Must

##### REQ-FE-071: MonthlyTrendChart

**Statement**: Bar chart shows last N months (default 6); X-axis
labels formatted as "MMM YY"; Y-axis as USD; bar color `#3B82F6`;
empty state.

**Source**: `Chapter8_FrontendDesign.md §8.8.2`

**Verification**: Read `MonthlyTrendChart.tsx`.

**Priority**: Must

##### REQ-FE-072: CumulativeLineChart

**Statement**: Line chart shows cumulative spending for the month
with a dashed budget reference line; line turns red when over
budget; empty state.

**Source**: `Chapter8_FrontendDesign.md §8.8.3`

**Verification**: Read `CumulativeLineChart.tsx`; run tests.

**Priority**: Must

##### REQ-FE-073: WeeklyHeatmap

**Statement**: Custom grid with 12 weeks × 7 days; color scale from
`#F3F4F6` (0) through blue shades; tooltip shows date and amount;
handles `max === 0` and missing days.

**Source**: `Chapter8_FrontendDesign.md §8.8.4`

**Verification**: Read `WeeklyHeatmap.tsx`; run tests.

**Priority**: Must

##### REQ-FE-074: BudgetProgress

**Statement**: Progress bar with color by percentage: green < 80%,
yellow 80-100%, red > 100%; caps width at 100%; shows "No budget
set" when budget is 0; displays formatted amounts.

**Source**: `Chapter8_FrontendDesign.md §8.8.5`

**Verification**: Read `BudgetProgress.tsx`; run tests.

**Priority**: Must

#### 12.9 Form Design

##### REQ-FE-080: validation schemas

**Statement**: Zod schemas: amountSchema (positive, ≤ 2 decimals,
max 9,999,999,999.99), expenseFormSchema, budgetFormSchema,
categoryFormSchema, loginFormSchema, registerFormSchema.

**Source**: `Chapter8_FrontendDesign.md §8.9.1`

**Verification**: Read `utils/validation.ts`.

**Priority**: Must

##### REQ-FE-081: ExpenseForm

**Statement**: ExpenseForm supports create and edit; uses React Hook
Form with Zod; shows field errors; disables submit while loading;
toasts on success and failure.

**Source**: `Chapter8_FrontendDesign.md §8.9.2`

**Verification**: Read `ExpenseForm.tsx`; run tests.

**Priority**: Must

##### REQ-FE-082: form behavior rules

**Statement**: Validate on blur and submit; disable submit while
loading; show field errors; show backend errors mapped to fields;
reset on success via onSuccess; preserve values on error.

**Source**: `Chapter8_FrontendDesign.md §8.9.3`

**Verification**: Read form components; run tests.

**Priority**: Must

#### 12.10 Design System

##### REQ-FE-090: color tokens

**Statement**: Design tokens: primary `#3B82F6`, success `#22C55E`,
warning `#EAB308`, danger `#EF4444`, background `#F9FAFB`, surface
white, border `#E5E7EB`, text primary `#111827`, secondary `#6B7280`,
muted `#9CA3AF`.

**Source**: `Chapter8_FrontendDesign.md §8.10.1`

**Verification**: Read `tailwind.config.js` and components.

**Priority**: Must

##### REQ-FE-091: typography

**Statement**: Page title `text-2xl font-semibold`, section title
`text-lg font-semibold`, KPI value `text-3xl font-bold`; system font
stack; `tabular-nums` for tables and KPIs.

**Source**: `Chapter8_FrontendDesign.md §8.10.2`

**Verification**: Read components.

**Priority**: Must

##### REQ-FE-092: spacing scale

**Statement**: Page padding `px-6 py-8`, card padding `p-6`, card
gap `gap-6`, section gap `space-y-8`, form gap `space-y-4`, max
width `max-w-7xl mx-auto`.

**Source**: `Chapter8_FrontendDesign.md §8.10.3`

**Verification**: Read components.

**Priority**: Should

##### REQ-FE-093: component specifications

**Statement**: Button variants (primary/secondary/danger/ghost) with
defined backgrounds; Card with border and shadow; Input with focus
ring and error state; Modal with overlay, centered panel, focus
trap, Esc; Toast top-right auto-dismiss 3s.

**Source**: `Chapter8_FrontendDesign.md §8.10.4`

**Verification**: Read `components/ui/`.

**Priority**: Must

##### REQ-FE-094: chart colors

**Statement**: Pie uses category colors; trend bars `#3B82F6`;
cumulative line `#3B82F6` normal and `#EF4444` over budget; budget
reference `#9CA3AF` dashed; heatmap five-step blue scale; progress
bar green/yellow/red.

**Source**: `Chapter8_FrontendDesign.md §8.10.5`

**Verification**: Read chart components.

**Priority**: Must

#### 12.11 Loading, Empty, Error States

##### REQ-FE-100: loading states

**Statement**: Full-page spinner for auth check; skeleton for
charts and tables; inline spinner for buttons; skeleton blocks for
KPI cards.

**Source**: `Chapter8_FrontendDesign.md §8.11.1`

**Verification**: Read components; observe while loading.

**Priority**: Must

##### REQ-FE-101: empty states

**Statement**: Each chart and list has a specific empty message;
EmptyState component takes icon, title, description, action.

**Source**: `Chapter8_FrontendDesign.md §8.11.2`

**Verification**: Read `EmptyState.tsx`; use the app with no data.

**Priority**: Must

##### REQ-FE-102: error states

**Statement**: Error handling maps 401/403/404/409/422/500/network
to specific UI; ErrorState component offers a retry button.

**Source**: `Chapter8_FrontendDesign.md §8.11.3`

**Verification**: Read `ErrorState.tsx`; simulate errors.

**Priority**: Must

##### REQ-FE-103: confirm dialog

**Statement**: Destructive actions use a ConfirmDialog with title,
description, confirm label, variant, onConfirm, onCancel.

**Source**: `Chapter8_FrontendDesign.md §8.11.4`

**Verification**: Read `ConfirmDialog.tsx`.

**Priority**: Must

#### 12.12 Accessibility

##### REQ-FE-110: accessibility checklist

**Statement**: Labels, accessible names, modal role/focus trap/Esc,
chart descriptions, contrast ≥ 4.5:1, keyboard navigation, skip
link, unique page titles, `html lang="en"`, visible focus, aria-
labels for icon buttons.

**Source**: `Chapter8_FrontendDesign.md §8.12.1`

**Verification**: Manual a11y check; inspect components.

**Priority**: Should

##### REQ-FE-111: modal focus management

**Statement**: On open, focus moves into the modal; on close, focus
returns to the trigger; Tab cycles; Esc closes.

**Source**: `Chapter8_FrontendDesign.md §8.12.2`

**Verification**: Read `Modal.tsx`.

**Priority**: Must

##### REQ-FE-112: chart accessibility

**Statement**: Each chart is wrapped in `<figure>` with a
`<figcaption>` and `role="img"` `aria-label` summarizing key values.

**Source**: `Chapter8_FrontendDesign.md §8.12.3`

**Verification**: Read chart components.

**Priority**: Should

#### 12.13 Performance

##### REQ-FE-120: performance techniques

**Statement**: Code splitting via `React.lazy` for pages and
charts; memoization for pure charts; query caching; debounced
inputs; server pagination; SVG charts; bundle analysis; asset
hashing; gzip.

**Source**: `Chapter8_FrontendDesign.md §8.13.1`

**Verification**: Read `App.tsx`; inspect build.

**Priority**: Should

##### REQ-FE-121: performance budget

**Statement**: Initial JS bundle < 300 KB gzipped, CSS < 30 KB
gzipped, Lighthouse performance > 85, FCP < 1.5s, TTI < 3s.

**Source**: `Chapter8_FrontendDesign.md §8.13.3`

**Verification**: Run `npm run build`; run Lighthouse.

**Priority**: Should

#### 12.14 Frontend Testing

##### REQ-FE-130: test structure

**Statement**: Tests live beside source with `.test.ts(x)`
suffixes; utils, charts, forms, and pages have tests.

**Source**: `Chapter8_FrontendDesign.md §8.14.1`

**Verification**: List test files.

**Priority**: Must

##### REQ-FE-131: coverage targets

**Statement**: Utils 90%+, charts 80%+, forms 80%+, pages 60%+,
API modules mocked (not tested directly).

**Source**: `Chapter8_FrontendDesign.md §8.14.2`

**Verification**: Run `npm run test -- --coverage`.

**Priority**: Should

##### REQ-FE-132: test examples

**Statement**: Tests exist for formatUSD, BudgetProgress color
logic, WeeklyHeatmap cells, CategoryPieChart merging, ExpenseForm
validation, LoginPage validation and errors.

**Source**: `Chapter8_FrontendDesign.md §8.14.3`

**Verification**: Read test files.

**Priority**: Must

##### REQ-FE-133: MSW setup

**Statement**: MSW handlers cover auth login, /auth/me,
/categories, /expenses, /dashboard/summary; setup.ts starts and
stops the server.

**Source**: `Chapter8_FrontendDesign.md §8.14.4`

**Verification**: Read `test/mocks/` and `test/setup.ts`.

**Priority**: Must

#### 12.15 Frontend Design Decisions

##### REQ-FE-140: build and language

**Statement**: Vite, TypeScript, Tailwind CSS, Recharts, React
Query, Context, React Hook Form + Zod, Axios, date-fns, React
Router v6.

**Source**: `Chapter8_FrontendDesign.md §8.15`

**Verification**: Read `package.json`.

**Priority**: Must

##### REQ-FE-141: token storage choice

**Statement**: Token stored in localStorage; documented trade-off.

**Source**: `Chapter8_FrontendDesign.md §8.15`

**Verification**: Read `client.ts`; read security notes.

**Priority**: Must

##### REQ-FE-142: centralized API choice

**Statement**: All API calls go through `src/api/`.

**Source**: `Chapter8_FrontendDesign.md §8.15`

**Verification**: Search frontend for direct fetch.

**Priority**: Must

##### REQ-FE-143: out-of-scope frontend features

**Statement**: Dark mode, i18n, SSR, PWA, analytics are not in MVP.

**Source**: `Chapter8_FrontendDesign.md §8.15`

**Verification**: Confirm absent in code.

**Priority**: Must

##### REQ-FE-144: accessibility and testing choice

**Statement**: WCAG 2.1 AA for forms and navigation; Vitest + RTL
for tests; MSW for mocking; coverage reported but not enforced.

**Source**: `Chapter8_FrontendDesign.md §8.15`

**Verification**: Read configs; inspect components.

**Priority**: Should

---

## Part 6: AI and Agent Requirements

### 13. AI Workflow Requirements

**Source**: `requirements/Chapter9_AIWorkflow.md`

#### 13.1 Overview

##### REQ-AI-001: four-layer workflow

**Statement**: The AI workflow has four layers: context, roles,
orchestration, and extension.

**Source**: `Chapter9_AIWorkflow.md §9.1`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

#### 13.2 Tool Selection

##### REQ-AI-010: primary tools

**Statement**: pi-agent is the primary coding agent; qwen3.8-27b is
the local LLM; plugins extend capabilities when needed.

**Source**: `Chapter9_AIWorkflow.md §9.2.1`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-011: confirmed capabilities

**Statement**: pi-agent reads AGENTS.md, discovers skills, launches
subagents, uses tools, performs file operations, and executes shell
commands.

**Source**: `Chapter9_AIWorkflow.md §9.2.2`

**Verification**: Read `docs/ai-workflow.md`; observe a session.

**Priority**: Must

##### REQ-AI-012: why local model

**Statement**: Local model chosen for data privacy, no API cost,
offline capability, reproducibility, and learning visibility.

**Source**: `Chapter9_AIWorkflow.md §9.2.3`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Should

##### REQ-AI-013: local model limitations

**Statement**: Smaller context window (keep AGENTS.md short),
slower inference (smaller issues), less capable at complex tasks
(more grooming), function calling may be less reliable (simpler
schemas).

**Source**: `Chapter9_AIWorkflow.md §9.2.4`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Should

#### 13.3 Context Engineering

##### REQ-AI-020: AGENTS.md

**Statement**: AGENTS.md contains commands, rules, and document
links; it is short and read at every session start.

**Source**: `Chapter9_AIWorkflow.md §9.3.1`

**Verification**: Read `AGENTS.md`.

**Priority**: Must

##### REQ-AI-021: CLAUDE.md

**Statement**: CLAUDE.md contains a single line `@AGENTS.md`.

**Source**: `Chapter9_AIWorkflow.md §9.3.2`

**Verification**: Read `CLAUDE.md`.

**Priority**: Must

##### REQ-AI-022: supporting documents

**Statement**: Supporting documents: process.md, architecture.md,
design-system.md, testing-guidelines.md, api.md, openapi.yaml, and
the three team role files.

**Source**: `Chapter9_AIWorkflow.md §9.3.3`

**Verification**: List `docs/`.

**Priority**: Must

##### REQ-AI-023: context loading strategy

**Statement**: The agent loads documents on demand based on task
type: backend endpoint, frontend UI, testing, PM grooming, QA
verification.

**Source**: `Chapter9_AIWorkflow.md §9.3.4`

**Verification**: Read AGENTS.md and docs structure.

**Priority**: Must

##### REQ-AI-024: living documents

**Statement**: When the agent makes a mistake, the correction is
written into the relevant document so it does not repeat.

**Source**: `Chapter9_AIWorkflow.md §9.3.5`

**Verification**: Read the correction log in `docs/ai-workflow.md`.

**Priority**: Must

#### 13.4 Role Definitions

##### REQ-AI-030: PM agent role

**Statement**: `docs/team/pm.md` defines the Product Manager role:
grooms tasks, rewrites using the task template, makes acceptance
criteria checkable, files follow-ups for out-of-scope items, and
does not write code.

**Source**: `Chapter9_AIWorkflow.md §9.4.1`

**Verification**: Read `docs/team/pm.md`.

**Priority**: Must

##### REQ-AI-031: SWE agent role

**Statement**: `docs/team/software-engineer.md` defines the
Software Engineer role: implements one groomed task, stays within
constraints, writes tests, does not close the issue, commits
regularly, and comments on the issue about what was done.

**Source**: `Chapter9_AIWorkflow.md §9.4.2`

**Verification**: Read `docs/team/software-engineer.md`.

**Priority**: Must

##### REQ-AI-032: QA agent role

**Statement**: `docs/team/qa-engineer.md` defines the QA role:
checks each acceptance criterion, runs tests, reports PASS or FAIL
with evidence, does not fix code.

**Source**: `Chapter9_AIWorkflow.md §9.4.3`

**Verification**: Read `docs/team/qa-engineer.md`.

**Priority**: Must

##### REQ-AI-033: role summary

**Statement**: PM produces groomed issue (no code); SWE produces
code + tests + commit; QA produces PASS/FAIL comment (no code).

**Source**: `Chapter9_AIWorkflow.md §9.4.4`

**Verification**: Read the three role files.

**Priority**: Must

#### 13.5 Orchestration

##### REQ-AI-040: orchestrator definition

**Statement**: `docs/process.md` defines the main session as the
orchestrator, with the PM → SWE → QA lifecycle and rules.

**Source**: `Chapter9_AIWorkflow.md §9.5.1`

**Verification**: Read `docs/process.md`.

**Priority**: Must

##### REQ-AI-041: workflow diagram

**Statement**: The workflow diagram shows Backlog → Orchestrator →
PM → SWE → QA, with FAIL looping back to SWE.

**Source**: `Chapter9_AIWorkflow.md §9.5.2`

**Verification**: Read `docs/process.md`.

**Priority**: Must

##### REQ-AI-042: sequential execution

**Statement**: MVP uses sequential execution: one issue flows
through PM → SWE → QA before the next issue starts.

**Source**: `Chapter9_AIWorkflow.md §9.5.3`

**Verification**: Read `docs/process.md`.

**Priority**: Must

##### REQ-AI-043: orchestrator commands

**Statement**: Commands: `Groom issue #N`, `Implement issue #N`,
`Test issue #N`, `/goal work through the backlog`.

**Source**: `Chapter9_AIWorkflow.md §9.5.4`

**Verification**: Read `docs/ai-workflow.md` for examples.

**Priority**: Must

##### REQ-AI-044: loop engineering

**Statement**: The `/goal` command keeps the orchestrator running
until the stop condition (all issues groomed, implemented, verified)
is met.

**Source**: `Chapter9_AIWorkflow.md §9.5.5`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-045: graph engineering

**Statement**: The workflow is a graph with PM, SWE, QA as nodes;
orchestrator enforces the graph; each agent runs in its own context.

**Source**: `Chapter9_AIWorkflow.md §9.5.6`

**Verification**: Read `docs/process.md` and `docs/ai-workflow.md`.

**Priority**: Must

#### 13.6 GitHub Issues as Backlog

##### REQ-AI-050: issue template

**Statement**: `docs/task-template.md` defines sections: Goal,
Acceptance criteria, Out of scope, Constraints.

**Source**: `Chapter9_AIWorkflow.md §9.6.1`

**Verification**: Read `docs/task-template.md`.

**Priority**: Must

##### REQ-AI-051: example groomed issue

**Statement**: A worked example shows a vague issue transformed
into a groomed issue with 14 acceptance criteria, out-of-scope
items, and constraints.

**Source**: `Chapter9_AIWorkflow.md §9.6.2`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-052: issue lifecycle

**Statement**: Issue lifecycle: open/ungroomed (human) → open/groomed
(PM) → open/implemented (SWE) → open/QA verdict (QA) → closed
(orchestrator).

**Source**: `Chapter9_AIWorkflow.md §9.6.3`

**Verification**: Read `docs/process.md`.

**Priority**: Must

#### 13.7 Skills

##### REQ-AI-060: skill format

**Statement**: Skills are markdown files with YAML frontmatter
containing name and description, stored in
`agent-capabilities/<name>/SKILL.md`.

**Source**: `Chapter9_AIWorkflow.md §9.7.1`

**Verification**: Read skill files.

**Priority**: Must

##### REQ-AI-061: monthly-report skill

**Statement**: The `monthly-report` skill generates a monthly
expense report with summary, top categories, and warnings.

**Source**: `Chapter9_AIWorkflow.md §9.7.2`

**Verification**: Read `agent-capabilities/monthly-report/SKILL.md`.

**Priority**: Must

##### REQ-AI-062: add-expense skill

**Statement**: The `add-expense` skill validates amount, calls
`add_expense`, and confirms success.

**Source**: `Chapter9_AIWorkflow.md §9.7.3`

**Verification**: Read `agent-capabilities/add-expense/SKILL.md`.

**Priority**: Must

##### REQ-AI-063: budget-check skill

**Statement**: The `budget-check` skill reports budget status and
warns if percentage > 80% or over budget.

**Source**: `Chapter9_AIWorkflow.md §9.7.4`

**Verification**: Read `agent-capabilities/budget-check/SKILL.md`.

**Priority**: Must

##### REQ-AI-064: skill discovery

**Statement**: Skills are discoverable via symlinks in
`.agents/skills/` (and `.claude/skills/` for Claude).

**Source**: `Chapter9_AIWorkflow.md §9.7.5`

**Verification**: `ls -la .agents/skills/`.

**Priority**: Must

##### REQ-AI-065: how skills are created

**Statement**: Skills emerge from doing the task first, correcting
the agent, then asking to save the workflow as a project-specific
skill.

**Source**: `Chapter9_AIWorkflow.md §9.7.6`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Should

#### 13.8 Subagents

##### REQ-AI-070: subagent structure

**Statement**: Subagent definitions are markdown files with YAML
frontmatter, stored in `custom-agent/<name>.md`, discoverable via
`.agents/agents/` symlinks.

**Source**: `Chapter9_AIWorkflow.md §9.8.1`

**Verification**: List `custom-agent/` and `.agents/agents/`.

**Priority**: Must

##### REQ-AI-071: finance-analyst subagent

**Statement**: `finance-analyst` analyzes spending patterns and
suggests adjustments; read-only.

**Source**: `Chapter9_AIWorkflow.md §9.8.2`

**Verification**: Read `custom-agent/finance-analyst.md`.

**Priority**: Must

##### REQ-AI-072: qa-reviewer subagent

**Statement**: `qa-reviewer` verifies work against acceptance
criteria and outputs PASS/FAIL; does not fix code.

**Source**: `Chapter9_AIWorkflow.md §9.8.3`

**Verification**: Read `custom-agent/qa-reviewer.md`.

**Priority**: Must

##### REQ-AI-073: subagent launch

**Statement**: Subagents launch with prompts like "Launch a
subagent to implement #12", "Launch QA for #12".

**Source**: `Chapter9_AIWorkflow.md §9.8.4`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-074: separate contexts

**Statement**: Subagents run in separate contexts to enable
independent verification and focused attention.

**Source**: `Chapter9_AIWorkflow.md §9.8.5`

**Verification**: Read `docs/process.md`.

**Priority**: Must

#### 13.9 MCP Server

##### REQ-AI-080: MCP purpose

**Statement**: The MCP server exposes backend operations as tools
the agent can call; it calls the backend API with the same JWT, not
the database.

**Source**: `Chapter9_AIWorkflow.md §9.9.1`

**Verification**: Read `mcp-server/server.py`.

**Priority**: Must

##### REQ-AI-081: MCP structure

**Statement**: MCP structure: server.py, auth.py, config.py,
tools/ with four tool modules.

**Source**: `Chapter9_AIWorkflow.md §9.9.2`

**Verification**: List `mcp-server/`.

**Priority**: Must

##### REQ-AI-082: MCP server entry

**Statement**: server.py defines `list_tools` returning four tool
definitions and `call_tool` dispatching to tool modules after JWT
verification.

**Source**: `Chapter9_AIWorkflow.md §9.9.3`

**Verification**: Read `mcp-server/server.py`.

**Priority**: Must

##### REQ-AI-083: MCP JWT verification

**Statement**: `verify_jwt` validates signature, exp, aud, iss,
checks `type == "access"`, returns `sub`.

**Source**: `Chapter9_AIWorkflow.md §9.9.4`

**Verification**: Read `mcp-server/auth.py`.

**Priority**: Must

##### REQ-AI-084: MCP tool implementation

**Statement**: Tools call the backend API via httpx with the Bearer
token, raising on non-2xx responses.

**Source**: `Chapter9_AIWorkflow.md §9.9.5`

**Verification**: Read `mcp-server/tools/`.

**Priority**: Must

##### REQ-AI-085: MCP tool list

**Statement**: Four tools: add_expense, get_budget_status,
monthly_summary, list_expenses.

**Source**: `Chapter9_AIWorkflow.md §9.9.6`

**Verification**: Read `mcp-server/server.py`.

**Priority**: Must

##### REQ-AI-086: MCP authentication flow

**Statement**: pi-agent reads `MCP_USER_TOKEN`, spawns the MCP
server as a subprocess, which reads `MCP_JWT_SECRET`,
`MCP_API_BASE_URL`, `MCP_USER_TOKEN`.

**Source**: `Chapter9_AIWorkflow.md §9.9.7`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-087: MCP calls API not database

**Statement**: Single permission layer, no schema duplication, same
behavior as frontend, easier testing, safer.

**Source**: `Chapter9_AIWorkflow.md §9.9.8`

**Verification**: Read `mcp-server/tools/`.

**Priority**: Must

##### REQ-AI-088: MCP server launch

**Statement**: Launched by pi-agent as a subprocess with
environment variables; example launch command documented.

**Source**: `Chapter9_AIWorkflow.md §9.9.9`

**Verification**: Read `mcp-server/README.md`.

**Priority**: Must

#### 13.10 Hooks

##### REQ-AI-090: hook purpose

**Statement**: Hooks are guardrails that run before agent actions,
preventing invalid operations.

**Source**: `Chapter9_AIWorkflow.md §9.10.1`

**Verification**: Read `agent-hooks/README.md`.

**Priority**: Must

##### REQ-AI-091: validate-amount hook

**Statement**: `validate_amount` validates the amount is a number,
positive, ≤ MAX_AMOUNT, ≤ 2 decimals; raises ValueError; returns
Decimal.

**Source**: `Chapter9_AIWorkflow.md §9.10.2`

**Verification**: Read `agent-hooks/validate-amount.py`.

**Priority**: Must

##### REQ-AI-092: validate-ownership hook

**Statement**: `validate_ownership` raises PermissionError if the
resource does not belong to the current user.

**Source**: `Chapter9_AIWorkflow.md §9.10.3`

**Verification**: Read `agent-hooks/validate-ownership.py`.

**Priority**: Must

##### REQ-AI-093: hook triggers

**Statement**: Hooks are triggered before MCP calls and are also
enforced in the backend (Pydantic, service layer).

**Source**: `Chapter9_AIWorkflow.md §9.10.4`

**Verification**: Read `mcp-server/tools/` and backend schemas.

**Priority**: Must

##### REQ-AI-094: hook README

**Statement**: `agent-hooks/README.md` documents trigger, checks,
failure behavior, and design notes.

**Source**: `Chapter9_AIWorkflow.md §9.10.5`

**Verification**: Read `agent-hooks/README.md`.

**Priority**: Must

#### 13.11 Permissions

##### REQ-AI-100: permissions matrix

**Statement**: `docs/permissions.md` defines user roles, resource
permissions, agent permissions by role, enforcement, and escalation
rules.

**Source**: `Chapter9_AIWorkflow.md §9.11.1`

**Verification**: Read `docs/permissions.md`.

**Priority**: Must

##### REQ-AI-101: defense in depth

**Statement**: Rules are enforced at hook, MCP, backend dependency,
backend service, backend test, and database layers.

**Source**: `Chapter9_AIWorkflow.md §9.11.2`

**Verification**: Read `docs/permissions.md`.

**Priority**: Must

#### 13.12 Real Session Records

##### REQ-AI-110: why record sessions

**Statement**: Session records provide evidence that AI tools were
used and reviewed.

**Source**: `Chapter9_AIWorkflow.md §9.12.1`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-111: session record format

**Statement**: Each session record includes date, tool, prompt,
agent output, human review, and commit.

**Source**: `Chapter9_AIWorkflow.md §9.12.2`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-112: session examples

**Statement**: Real sessions exist for grooming, implementing, QA
fail, fixing, and re-verification.

**Source**: `Chapter9_AIWorkflow.md §9.12.3–9.12.5`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-113: session coverage

**Statement**: Sessions are recorded across spec, auth, CRUD,
dashboard, frontend, testing, security, and deployment phases.

**Source**: `Chapter9_AIWorkflow.md §9.12.6`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

#### 13.13 Correction Log

##### REQ-AI-120: correction log format

**Statement**: The correction log records date, issue, AI output,
correction, and lesson.

**Source**: `Chapter9_AIWorkflow.md §9.13.2`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-121: correction examples

**Statement**: Six example corrections are recorded, covering
pagination, Decimal, isolation, aggregation, heatmap week start,
and referential integrity.

**Source**: `Chapter9_AIWorkflow.md §9.13.3`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-122: document updates from corrections

**Statement**: Each correction updates the relevant document
(AGENTS.md, SWE role, testing guidelines, design system, task
template).

**Source**: `Chapter9_AIWorkflow.md §9.13.4`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

#### 13.14 Data Policy

##### REQ-AI-130: data policy summary

**Statement**: All code, prompts, and context stay on the local
machine; no data is sent to cloud LLM providers.

**Source**: `Chapter9_AIWorkflow.md §9.14.1`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

##### REQ-AI-131: what the agent sees

**Statement**: The agent sees source code, tests, docs, OpenAPI,
seed data. It never sees real user data, production database,
secrets, or JWT tokens.

**Source**: `Chapter9_AIWorkflow.md §9.14.2`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

##### REQ-AI-132: what the agent produces

**Statement**: Outputs (code, tests, commits, docs, security
notes) all require human review.

**Source**: `Chapter9_AIWorkflow.md §9.14.3`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-133: data flow

**Statement**: Data flow diagram shows local-only processing with
no connection to cloud LLMs, external AI services, or production
databases.

**Source**: `Chapter9_AIWorkflow.md §9.14.4`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

##### REQ-AI-134: compliance notes

**Statement**: Data residency local, no PII, no secrets in context,
audit via session records, reproducibility via same model version.

**Source**: `Chapter9_AIWorkflow.md §9.14.5`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Should

#### 13.15 AI Workflow Design Decisions

##### REQ-AI-140: agent and model choice

**Statement**: pi-agent with qwen3.8-27b for local, no-cost,
controllable workflow.

**Source**: `Chapter9_AIWorkflow.md §9.15`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-AI-141: context and roles choice

**Statement**: AGENTS.md as tool-agnostic context; PM/SWE/QA roles
match course Part 1.

**Source**: `Chapter9_AIWorkflow.md §9.15`

**Verification**: Read `AGENTS.md` and `docs/process.md`.

**Priority**: Must

##### REQ-AI-142: orchestration choice

**Statement**: Main session as orchestrator; GitHub Issues as
backlog; sequential execution for MVP.

**Source**: `Chapter9_AIWorkflow.md §9.15`

**Verification**: Read `docs/process.md`.

**Priority**: Must

##### REQ-AI-143: extension choice

**Statement**: Three skills, two subagents, four MCP tools, two
hooks, JWT auth, data policy local-only.

**Source**: `Chapter9_AIWorkflow.md §9.15`

**Verification**: List each directory.

**Priority**: Must

---

### 14. Agent Extension Pack Requirements

**Source**: `requirements/Chapter10_AgentExtensionPack.md`

#### 14.1 Overview

##### REQ-EXT-001: five components

**Statement**: The pack has five components: skills, hooks, MCP
server, subagents, and documentation.

**Source**: `Chapter10_AgentExtensionPack.md §10.1`

**Verification**: List each directory.

**Priority**: Must

##### REQ-EXT-002: Criterion 12 mapping

**Statement**: The pack maps to Criterion 12 requirements: project
instructions (AGENTS.md), reusable workflow (process.md), subagent
(finance-analyst, qa-reviewer), MCP tool/server, hook/guardrail,
permission notes.

**Source**: `Chapter10_AgentExtensionPack.md §10.1.1`

**Verification**: Read `docs/agent-extension-pack.md`.

**Priority**: Must

##### REQ-EXT-003: directory layout

**Statement**: Directories: `agent-capabilities/`, `agent-hooks/`,
`mcp-server/`, `custom-agent/`, `docs/`, and `.agents/` symlinks.

**Source**: `Chapter10_AgentExtensionPack.md §10.1.2`

**Verification**: List repository root.

**Priority**: Must

##### REQ-EXT-004: symlinks

**Statement**: Symlinks in `.agents/skills/` and `.agents/agents/`
connect canonical directories to the agent's expected discovery
paths.

**Source**: `Chapter10_AgentExtensionPack.md §10.1.3`

**Verification**: `ls -la .agents/skills/` and `ls -la .agents/agents/`.

**Priority**: Must

#### 14.2 Skills

##### REQ-EXT-010: skill format

**Statement**: Skills are markdown files with YAML frontmatter
containing name and description.

**Source**: `Chapter10_AgentExtensionPack.md §10.2.1`

**Verification**: Read skill files.

**Priority**: Must

##### REQ-EXT-011: monthly-report skill content

**Statement**: The skill documents when to use, steps, report
template, warnings, and notes.

**Source**: `Chapter10_AgentExtensionPack.md §10.2.2`

**Verification**: Read `agent-capabilities/monthly-report/SKILL.md`.

**Priority**: Must

##### REQ-EXT-012: add-expense skill content

**Statement**: The skill documents when to use, steps, constraints,
and an example.

**Source**: `Chapter10_AgentExtensionPack.md §10.2.3`

**Verification**: Read `agent-capabilities/add-expense/SKILL.md`.

**Priority**: Must

##### REQ-EXT-013: budget-check skill content

**Statement**: The skill documents when to use, steps, and output
template.

**Source**: `Chapter10_AgentExtensionPack.md §10.2.4`

**Verification**: Read `agent-capabilities/budget-check/SKILL.md`.

**Priority**: Must

##### REQ-EXT-014: skill discovery

**Statement**: Discovery via auto-discovery at session start,
natural-language invocation, and explicit command.

**Source**: `Chapter10_AgentExtensionPack.md §10.2.5`

**Verification**: Read `docs/agent-extension-pack.md`.

**Priority**: Must

##### REQ-EXT-015: skill design principles

**Statement**: One procedure per skill, clear "When to Use",
numbered steps, explicit constraints, no side effects in read-only
skills, templates for output.

**Source**: `Chapter10_AgentExtensionPack.md §10.2.6`

**Verification**: Read skill files.

**Priority**: Should

#### 14.3 Hooks

##### REQ-EXT-020: hook purpose

**Statement**: Hooks validate inputs and raise errors when rules
are violated; pure functions with no side effects.

**Source**: `Chapter10_AgentExtensionPack.md §10.3.1`

**Verification**: Read `agent-hooks/README.md`.

**Priority**: Must

##### REQ-EXT-021: validate-amount hook

**Statement**: `validate_amount` validates present, valid number,
positive, ≤ MAX_AMOUNT, ≤ 2 decimals; returns Decimal; raises
ValueError.

**Source**: `Chapter10_AgentExtensionPack.md §10.3.2`

**Verification**: Read `agent-hooks/validate-amount.py`; run tests.

**Priority**: Must

##### REQ-EXT-022: validate-ownership hook

**Statement**: `validate_ownership` raises PermissionError when
user IDs do not match or are None.

**Source**: `Chapter10_AgentExtensionPack.md §10.3.3`

**Verification**: Read `agent-hooks/validate-ownership.py`; run tests.

**Priority**: Must

##### REQ-EXT-023: hook triggers

**Statement**: Hooks triggered before MCP calls and in backend
(Pydantic schemas and service layer).

**Source**: `Chapter10_AgentExtensionPack.md §10.3.4`

**Verification**: Read `mcp-server/tools/` and backend code.

**Priority**: Must

##### REQ-EXT-024: hook README

**Statement**: `agent-hooks/README.md` documents both hooks'
triggers, checks, failure behavior, agent behavior, and design
notes.

**Source**: `Chapter10_AgentExtensionPack.md §10.3.5`

**Verification**: Read `agent-hooks/README.md`.

**Priority**: Must

##### REQ-EXT-025: defense in depth

**Statement**: Rules enforced at hook, MCP, backend schema,
backend service, and database layers.

**Source**: `Chapter10_AgentExtensionPack.md §10.3.6`

**Verification**: Read `docs/permissions.md`.

**Priority**: Must

#### 14.4 MCP Server

##### REQ-EXT-030: MCP purpose

**Statement**: MCP server exposes backend operations as tools;
authenticates with JWT; never accesses the database directly.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.1`

**Verification**: Read `mcp-server/server.py`.

**Priority**: Must

##### REQ-EXT-031: MCP architecture

**Statement**: pi-agent ↔ MCP server (stdio) ↔ backend API ↔
database.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.2`

**Verification**: Read `mcp-server/README.md`.

**Priority**: Must

##### REQ-EXT-032: MCP configuration

**Statement**: `config.py` reads `MCP_JWT_SECRET`,
`MCP_API_BASE_URL`, `MCP_USER_TOKEN`, and defines JWT algorithm,
issuer, audience.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.3`

**Verification**: Read `mcp-server/config.py`.

**Priority**: Must

##### REQ-EXT-033: MCP authentication

**Statement**: `verify_jwt` validates signature, exp, aud, iss,
`type == "access"`, returns sub; `get_user_token` reads from env.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.4`

**Verification**: Read `mcp-server/auth.py`.

**Priority**: Must

##### REQ-EXT-034: add_expense tool

**Statement**: `add_expense` validates amount, builds payload,
POSTs to `/expenses` with Bearer token.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.5`

**Verification**: Read `mcp-server/tools/add_expense.py`.

**Priority**: Must

##### REQ-EXT-035: get_budget_status tool

**Statement**: `get_budget_status` calls `/dashboard/summary`,
returns simplified shape.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.6`

**Verification**: Read `mcp-server/tools/get_budget_status.py`.

**Priority**: Must

##### REQ-EXT-036: monthly_summary tool

**Statement**: `monthly_summary` calls `/dashboard/by-category`.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.7`

**Verification**: Read `mcp-server/tools/monthly_summary.py`.

**Priority**: Must

##### REQ-EXT-037: list_expenses tool

**Statement**: `list_expenses` calls `/expenses` with optional
filters; `limit` maps to `page_size`.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.8`

**Verification**: Read `mcp-server/tools/list_expenses.py`.

**Priority**: Must

##### REQ-EXT-038: tool schemas

**Statement**: Four tool schemas defined with strict types,
required fields, and constraints.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.9`

**Verification**: Read `mcp-server/server.py`.

**Priority**: Must

##### REQ-EXT-039: MCP README

**Statement**: `mcp-server/README.md` documents tools,
authentication, environment variables, running instructions, and
design.

**Source**: `Chapter10_AgentExtensionPack.md §10.4.10`

**Verification**: Read `mcp-server/README.md`.

**Priority**: Must

#### 14.5 Subagents

##### REQ-EXT-040: subagent purpose

**Statement**: Subagents run in separate contexts with clear roles
for independent verification and focused analysis.

**Source**: `Chapter10_AgentExtensionPack.md §10.5.1`

**Verification**: Read `docs/agent-extension-pack.md`.

**Priority**: Must

##### REQ-EXT-041: finance-analyst subagent

**Statement**: `finance-analyst` has input, steps, output template,
limitations, and rules (read-only, no raw IDs).

**Source**: `Chapter10_AgentExtensionPack.md §10.5.2`

**Verification**: Read `custom-agent/finance-analyst.md`.

**Priority**: Must

##### REQ-EXT-042: qa-reviewer subagent

**Statement**: `qa-reviewer` has steps, output format, and rules
(do not fix, do not modify code, include test command).

**Source**: `Chapter10_AgentExtensionPack.md §10.5.3`

**Verification**: Read `custom-agent/qa-reviewer.md`.

**Priority**: Must

##### REQ-EXT-043: subagent launch commands

**Statement**: Commands: "Launch a subagent to implement #12",
"Launch software engineer for #12", "Launch QA for #12", "Launch
finance analyst for 2026-10".

**Source**: `Chapter10_AgentExtensionPack.md §10.5.4`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-EXT-044: subagent isolation

**Statement**: Fresh context, no orchestrator history, output posted
back, tools restricted by role, permissions enforced by MCP and
backend.

**Source**: `Chapter10_AgentExtensionPack.md §10.5.5`

**Verification**: Read `docs/process.md`.

**Priority**: Must

#### 14.6 Documentation

##### REQ-EXT-050: agent-extension-pack.md purpose

**Statement**: This document explains the whole pack in one place
so a reviewer can understand it from one file.

**Source**: `Chapter10_AgentExtensionPack.md §10.6.1`

**Verification**: Read `docs/agent-extension-pack.md`.

**Priority**: Must

##### REQ-EXT-051: agent-extension-pack.md content

**Statement**: Contents include skills, hooks, MCP server,
subagents, permissions, and design principles.

**Source**: `Chapter10_AgentExtensionPack.md §10.6.2`

**Verification**: Read `docs/agent-extension-pack.md`.

**Priority**: Must

#### 14.7 Permissions

##### REQ-EXT-060: permissions.md content

**Statement**: `docs/permissions.md` contains user roles, resource
permissions, agent permissions by role, skill permissions, subagent
permissions, enforcement layers, forbidden actions, and escalation
rules.

**Source**: `Chapter10_AgentExtensionPack.md §10.7.1`

**Verification**: Read `docs/permissions.md`.

**Priority**: Must

#### 14.8 Verification

##### REQ-EXT-070: verification checklist

**Statement**: The pack can be verified by checking skills, hooks,
MCP server, subagents, symlinks, and documentation.

**Source**: `Chapter10_AgentExtensionPack.md §10.8.1`

**Verification**: Read `docs/agent-extension-pack.md`.

**Priority**: Must

##### REQ-EXT-071: manual test commands

**Statement**: Documented commands test skills, hooks, MCP server,
subagents, symlinks, and documentation.

**Source**: `Chapter10_AgentExtensionPack.md §10.8.2`

**Verification**: Run the commands.

**Priority**: Must

##### REQ-EXT-072: automated verification

**Statement**: `backend/tests/integration/test_agent_hooks.py`
imports and tests both hooks.

**Source**: `Chapter10_AgentExtensionPack.md §10.8.3`

**Verification**: Run the test file.

**Priority**: Must

#### 14.9 Extension Pack Design Decisions

##### REQ-EXT-080: directory choices

**Statement**: Skills in `agent-capabilities/`, hooks in
`agent-hooks/`, MCP in `mcp-server/`, subagents in `custom-agent/`,
symlinks in `.agents/`.

**Source**: `Chapter10_AgentExtensionPack.md §10.9`

**Verification**: List each directory.

**Priority**: Must

##### REQ-EXT-081: MCP design choices

**Statement**: stdio transport, JWT auth, API access (not database).

**Source**: `Chapter10_AgentExtensionPack.md §10.9`

**Verification**: Read `mcp-server/README.md`.

**Priority**: Must

##### REQ-EXT-082: read-only analyst

**Statement**: `finance-analyst` is read-only for safety;
`qa-reviewer` does not fix.

**Source**: `Chapter10_AgentExtensionPack.md §10.9`

**Verification**: Read subagent files.

**Priority**: Must

##### REQ-EXT-083: two documentation files

**Statement**: Extension pack overview and permissions matrix are
separate documents.

**Source**: `Chapter10_AgentExtensionPack.md §10.9`

**Verification**: Read `docs/agent-extension-pack.md` and
`docs/permissions.md`.

**Priority**: Must

---

## Part 7: Quality Requirements

### 15. Testing Strategy Requirements

**Source**: `requirements/Chapter11_TestingStrategy.md`

#### 15.1 Overview

##### REQ-TEST-001: four test layers

**Statement**: Testing is organized into four layers: backend unit
(pytest), backend integration (pytest + httpx), frontend
unit/component (Vitest + RTL), and end-to-end (Playwright).

**Source**: `Chapter11_TestingStrategy.md §11.1`

**Verification**: List test directories.

**Priority**: Must

##### REQ-TEST-002: testing principles

**Statement**: Tests assert behavior not implementation, one
assertion per concept, independent, deterministic, fast by default,
realistic integration, isolated E2E.

**Source**: `Chapter11_TestingStrategy.md §11.1.1`

**Verification**: Read tests; run twice to check determinism.

**Priority**: Must

##### REQ-TEST-003: coverage policy

**Statement**: Coverage is reported but not enforced. Targets:
backend unit 80%+, backend integration 70%+, frontend unit 80%+,
frontend components 70%+, E2E core flows.

**Source**: `Chapter11_TestingStrategy.md §11.1.2`

**Verification**: Run coverage commands.

**Priority**: Should

#### 15.2 Backend Unit Tests

##### REQ-TEST-010: backend test structure

**Statement**: Backend tests live in `backend/tests/` with
`conftest.py`, `unit/`, and `integration/` subdirectories.

**Source**: `Chapter11_TestingStrategy.md §11.2.1`

**Verification**: List `backend/tests/`.

**Priority**: Must

##### REQ-TEST-011: test fixtures

**Statement**: `conftest.py` provides `db_session` (in-memory
SQLite with StaticPool), `user_a`, `user_b`, `system_category`,
`client`, `auth_headers`, `auth_headers_b`.

**Source**: `Chapter11_TestingStrategy.md §11.2.2` and `§11.3.1`

**Verification**: Read `conftest.py`.

**Priority**: Must

##### REQ-TEST-012: password tests

**Statement**: `test_password.py` verifies hash is not plain, hash
starts with `$2b$`, correct password verifies, wrong password fails,
hash is salted.

**Source**: `Chapter11_TestingStrategy.md §11.2.3`

**Verification**: Read `test_password.py`; run tests.

**Priority**: Must

##### REQ-TEST-013: JWT tests

**Statement**: `test_jwt.py` verifies claims, valid token decoding,
expired token raises, wrong audience raises, wrong issuer raises.

**Source**: `Chapter11_TestingStrategy.md §11.2.4`

**Verification**: Read `test_jwt.py`; run tests.

**Priority**: Must

##### REQ-TEST-014: auth service tests

**Statement**: `test_auth_service.py` verifies register success,
duplicate email, duplicate username, login success, wrong password,
nonexistent email.

**Source**: `Chapter11_TestingStrategy.md §11.2.5`

**Verification**: Read `test_auth_service.py`; run tests.

**Priority**: Must

##### REQ-TEST-015: expense service tests

**Statement**: `test_expense_service.py` verifies create, audit log
on create, user isolation on list, audit log on update, cross-user
delete returns 404.

**Source**: `Chapter11_TestingStrategy.md §11.2.6`

**Verification**: Read `test_expense_service.py`; run tests.

**Priority**: Must

##### REQ-TEST-016: budget service tests

**Statement**: `test_budget_service.py` verifies create, upsert,
nonexistent returns None, delete nonexistent returns 404, invalid
year_month format.

**Source**: `Chapter11_TestingStrategy.md §11.2.7`

**Verification**: Read `test_budget_service.py`; run tests.

**Priority**: Must

##### REQ-TEST-017: dashboard service tests

**Statement**: `test_dashboard_service.py` verifies summary with no
expenses, summary with budget and expenses, over budget, by-category
aggregation, trend includes empty months, cumulative last day equals
total, heatmap 7 days per week, recent limit.

**Source**: `Chapter11_TestingStrategy.md §11.2.8`

**Verification**: Read `test_dashboard_service.py`; run tests.

**Priority**: Must

##### REQ-TEST-018: decimal helper tests

**Statement**: `test_decimal_helpers.py` verifies `to_decimal` from
string, from float (quantizes), from None, from int, quantizes to
two places.

**Source**: `Chapter11_TestingStrategy.md §11.2.9`

**Verification**: Read `test_decimal_helpers.py`; run tests.

**Priority**: Must

#### 15.3 Backend Integration Tests

##### REQ-TEST-020: auth API tests

**Statement**: `test_auth_api.py` verifies register success,
duplicate email, short password, login success, wrong password, me
with valid token, me without token, me with invalid token.

**Source**: `Chapter11_TestingStrategy.md §11.3.2`

**Verification**: Read `test_auth_api.py`; run tests.

**Priority**: Must

##### REQ-TEST-021: expenses API tests

**Statement**: `test_expenses_api.py` verifies create, negative
amount, zero amount, three decimals, requires auth, pagination,
invalid page, page_size too large, update, delete.

**Source**: `Chapter11_TestingStrategy.md §11.3.3`

**Verification**: Read `test_expenses_api.py`; run tests.

**Priority**: Must

##### REQ-TEST-022: budgets API tests

**Statement**: `test_budgets_api.py` verifies set budget, get
nonexistent returns 0, invalid year_month, delete budget, delete
nonexistent returns 404.

**Source**: `Chapter11_TestingStrategy.md §11.3.4`

**Verification**: Read `test_budgets_api.py`; run tests.

**Priority**: Must

##### REQ-TEST-023: dashboard API tests

**Statement**: `test_dashboard_api.py` verifies summary empty,
by-category empty, trend default six months, cumulative returns all
days, heatmap returns weeks, recent default ten.

**Source**: `Chapter11_TestingStrategy.md §11.3.5`

**Verification**: Read `test_dashboard_api.py`; run tests.

**Priority**: Must

##### REQ-TEST-024: isolation tests

**Statement**: `test_isolation.py` verifies user cannot read,
update, or delete another user's expense (404), user sees only own
expenses, budget isolation.

**Source**: `Chapter11_TestingStrategy.md §11.3.6`

**Verification**: Read `test_isolation.py`; run tests.

**Priority**: Must

##### REQ-TEST-025: health API test

**Statement**: `test_health_api.py` verifies status in (ok,
degraded), database in (postgresql, sqlite), fallback_active is bool,
version present.

**Source**: `Chapter11_TestingStrategy.md §11.3.7`

**Verification**: Read `test_health_api.py`; run tests.

**Priority**: Must

##### REQ-TEST-026: agent hooks test

**Statement**: `test_agent_hooks.py` verifies validate_amount
accepts valid and rejects negative, zero, three decimals,
non-number, over-max; validate_ownership accepts same user and
rejects different user.

**Source**: `Chapter11_TestingStrategy.md §11.3.8`

**Verification**: Read `test_agent_hooks.py`; run tests.

**Priority**: Must

#### 15.4 Frontend Tests

##### REQ-TEST-030: frontend test setup

**Statement**: `frontend/src/test/setup.ts` starts and stops MSW,
resets handlers after each test.

**Source**: `Chapter11_TestingStrategy.md §11.4.1`

**Verification**: Read `setup.ts`.

**Priority**: Must

##### REQ-TEST-031: format tests

**Statement**: `format.test.ts` verifies `formatUSD` for integer,
decimal, large with commas, zero, negative; `formatPercent` for
whole, decimal, null; `formatMonth`.

**Source**: `Chapter11_TestingStrategy.md §11.4.2`

**Verification**: Read `format.test.ts`; run tests.

**Priority**: Must

##### REQ-TEST-032: date tests

**Statement**: `date.test.ts` verifies `currentYearMonth` format,
`shiftMonth` forward/backward/year boundaries, `monthRange`.

**Source**: `Chapter11_TestingStrategy.md §11.4.2`

**Verification**: Read `date.test.ts`; run tests.

**Priority**: Must

##### REQ-TEST-033: validation tests

**Statement**: `validation.test.ts` verifies `amountSchema` for
valid, integer, negative, zero, three decimals, non-numeric;
`expenseFormSchema` for valid, invalid category_id, long note.

**Source**: `Chapter11_TestingStrategy.md §11.4.2`

**Verification**: Read `validation.test.ts`; run tests.

**Priority**: Must

##### REQ-TEST-034: BudgetProgress tests

**Statement**: `BudgetProgress.test.tsx` verifies green under 80%,
yellow 80-100%, red over 100%, caps at 100%, "No budget set" when
budget 0, formatted amounts.

**Source**: `Chapter11_TestingStrategy.md §11.4.3`

**Verification**: Read `BudgetProgress.test.tsx`; run tests.

**Priority**: Must

##### REQ-TEST-035: WeeklyHeatmap tests

**Statement**: `WeeklyHeatmap.test.tsx` verifies 7 days rendered,
grey for zero, handles max zero, shows skeleton when loading.

**Source**: `Chapter11_TestingStrategy.md §11.4.3`

**Verification**: Read `WeeklyHeatmap.test.tsx`; run tests.

**Priority**: Must

##### REQ-TEST-036: CategoryPieChart tests

**Statement**: `CategoryPieChart.test.tsx` verifies empty state,
renders with data, merges to Other when > 6 categories.

**Source**: `Chapter11_TestingStrategy.md §11.4.3`

**Verification**: Read `CategoryPieChart.test.tsx`; run tests.

**Priority**: Must

##### REQ-TEST-037: ExpenseForm tests

**Statement**: `ExpenseForm.test.tsx` verifies empty amount error,
negative amount error, three decimals error, cancel callback.

**Source**: `Chapter11_TestingStrategy.md §11.4.3`

**Verification**: Read `ExpenseForm.test.tsx`; run tests.

**Priority**: Must

##### REQ-TEST-038: LoginPage tests

**Statement**: `LoginPage.test.tsx` verifies fields render, invalid
email error, invalid credentials error.

**Source**: `Chapter11_TestingStrategy.md §11.4.3`

**Verification**: Read `LoginPage.test.tsx`; run tests.

**Priority**: Must

##### REQ-TEST-039: MSW handlers

**Statement**: MSW handlers cover `/auth/login`, `/auth/me`,
`/categories`, `/expenses`, `/dashboard/summary`.

**Source**: `Chapter11_TestingStrategy.md §11.4.4`

**Verification**: Read `test/mocks/handlers.ts`.

**Priority**: Must

#### 15.5 End-to-End Tests

##### REQ-TEST-040: Playwright setup

**Statement**: `e2e/` contains tests/, fixtures/, and
`playwright.config.ts` with baseURL, timeout 60s, retries 1,
workers 1, HTML reporter, trace on first retry, screenshot on
failure.

**Source**: `Chapter11_TestingStrategy.md §11.5.1`

**Verification**: Read `playwright.config.ts`.

**Priority**: Must

##### REQ-TEST-041: E2E fixtures

**Statement**: `fixtures/users.ts` provides `uniqueUser`;
`fixtures/helpers.ts` provides `registerUser`, `loginUser`,
`addExpense`, `setBudget`.

**Source**: `Chapter11_TestingStrategy.md §11.5.2`

**Verification**: Read fixture files.

**Priority**: Must

##### REQ-TEST-042: happy path test

**Statement**: `happy-path.spec.ts` runs through register, three
expenses, set budget, verify dashboard totals, all five charts
visible, recent shows three items, edit, verify update, delete,
verify update, logout.

**Source**: `Chapter11_TestingStrategy.md §11.5.3`

**Verification**: Read `happy-path.spec.ts`; run E2E.

**Priority**: Must

##### REQ-TEST-043: isolation test

**Statement**: `isolation.spec.ts` runs two browser contexts:
User A registers and adds expense; User B registers and sees empty
dashboard and no expense rows.

**Source**: `Chapter11_TestingStrategy.md §11.5.4`

**Verification**: Read `isolation.spec.ts`; run E2E.

**Priority**: Must

##### REQ-TEST-044: month switch test

**Statement**: `month-switch.spec.ts` adds expenses in two months,
switches months, verifies totals update, switches back, verifies.

**Source**: `Chapter11_TestingStrategy.md §11.5.5`

**Verification**: Read `month-switch.spec.ts`; run E2E.

**Priority**: Must

##### REQ-TEST-045: E2E data isolation

**Statement**: Each E2E test creates a unique user with timestamp
and random ID; no cleanup between tests; optional cleanup SQL
documented.

**Source**: `Chapter11_TestingStrategy.md §11.5.6`

**Verification**: Read fixtures; read cleanup SQL.

**Priority**: Must

#### 15.6 Test Execution

##### REQ-TEST-050: Makefile targets

**Statement**: Makefile targets: `test`, `test-backend`,
`test-backend-unit`, `test-backend-integration`, `test-backend-cov`,
`test-frontend`, `test-frontend-cov`, `e2e`.

**Source**: `Chapter11_TestingStrategy.md §11.6.1`

**Verification**: Read `Makefile`.

**Priority**: Must

##### REQ-TEST-051: CI execution

**Statement**: `ci.yml` runs `make test-backend` and
`make test-frontend`; `e2e.yml` runs `make e2e`.

**Source**: `Chapter11_TestingStrategy.md §11.6.2`

**Verification**: Read workflow files.

**Priority**: Must

#### 15.7 Test Data Strategy

##### REQ-TEST-060: backend test data

**Statement**: Backend unit and integration tests use in-memory
SQLite with seeded system categories; test users created per test
via fixtures.

**Source**: `Chapter11_TestingStrategy.md §11.7.1`

**Verification**: Read `conftest.py`.

**Priority**: Must

##### REQ-TEST-061: frontend test data

**Statement**: Frontend unit tests use pure functions; component
tests use MSW handlers with fixed data; page tests use MSW variants.

**Source**: `Chapter11_TestingStrategy.md §11.7.2`

**Verification**: Read MSW handlers and tests.

**Priority**: Must

##### REQ-TEST-062: E2E test data

**Statement**: E2E tests use the real backend and database with
unique users per test.

**Source**: `Chapter11_TestingStrategy.md §11.7.3`

**Verification**: Read E2E fixtures.

**Priority**: Must

##### REQ-TEST-063: SQLite for backend tests rationale

**Statement**: SQLite in-memory is fast, isolated, needs no
external dependency, and uses the same ORM; PostgreSQL is tested in
CI via Docker Compose.

**Source**: `Chapter11_TestingStrategy.md §11.7.4`

**Verification**: Read `docs/testing-guidelines.md`.

**Priority**: Should

#### 15.8 Not Tested

##### REQ-TEST-070: not tested list

**Statement**: Render deployment, cold start, UptimeRobot, browser
compatibility, load testing, security scanning, visual regression,
accessibility automation are not tested.

**Source**: `Chapter11_TestingStrategy.md §11.8`

**Verification**: Read `docs/testing-guidelines.md`.

**Priority**: Should

#### 15.9 Testing Design Decisions

##### REQ-TEST-080: framework choices

**Statement**: pytest for backend, pytest + TestClient for
integration, SQLite in-memory, Vitest for frontend, RTL for
components, MSW for API mocking, Playwright for E2E.

**Source**: `Chapter11_TestingStrategy.md §11.9`

**Verification**: Read test configs.

**Priority**: Must

##### REQ-TEST-081: execution choices

**Statement**: Coverage reported not enforced; CI runs unit +
integration; E2E only on main; per-test fixtures; Decimal
comparison; fixed dates.

**Source**: `Chapter11_TestingStrategy.md §11.9`

**Verification**: Read workflows and tests.

**Priority**: Must

##### REQ-TEST-082: error testing

**Statement**: Error tests assert both status code and error code.

**Source**: `Chapter11_TestingStrategy.md §11.9`

**Verification**: Read integration tests.

**Priority**: Must

---

### 16. Security and Audit Requirements

**Source**: `requirements/Chapter12_SecurityandAudit.md`

#### 16.1 Overview

##### REQ-SEC-001: Criterion 13 mapping

**Statement**: The project provides PR audit output, deterministic
security scan findings, agent/extension security notes, operational
diagnosis output, and an AI tool/data policy.

**Source**: `Chapter12_SecurityandAudit.md §12.1.1`

**Verification**: List `security/` and `ops/diagnosis.md`.

**Priority**: Must

##### REQ-SEC-002: security layers

**Statement**: Security layers: network (HTTPS, CORS),
authentication (JWT HS256), password (bcrypt), authorization
(user_id filter), data isolation (404), input validation
(Pydantic), amount integrity (Decimal), audit (same transaction),
secrets (env vars), dependencies (scanned), agent (hooks, JWT,
permissions), data policy (local model).

**Source**: `Chapter12_SecurityandAudit.md §12.1.2`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-003: security directory layout

**Statement**: `security/` contains pr-audit.md,
gitleaks-report.json, semgrep-report.json, trivy-report.json,
pip-audit-report.txt, npm-audit-report.txt,
agent-security-notes.md, ai-tool-data-policy.md.

**Source**: `Chapter12_SecurityandAudit.md §12.1.3`

**Verification**: List `security/`.

**Priority**: Must

#### 16.2 Threat Model

##### REQ-SEC-010: assets

**Statement**: Assets: user credentials (high), JWT secret (high),
user expense data (medium), user budget data (medium), audit logs
(medium), source code (low), configuration (medium).

**Source**: `Chapter12_SecurityandAudit.md §12.2.1`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-011: threat actors

**Statement**: Threat actors: unauthenticated attacker,
authenticated malicious user, compromised dependency, misconfigured
deployment, malicious agent input.

**Source**: `Chapter12_SecurityandAudit.md §12.2.2`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-012: threats and mitigations

**Statement**: 15 threats documented with mitigations: brute force,
token forgery, replay, cross-user access, SQL injection, XSS, CSRF,
secret leakage, dependency vulnerability, agent exfiltration,
prompt injection, audit tampering, amount precision, enumeration,
DoS.

**Source**: `Chapter12_SecurityandAudit.md §12.2.3`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-013: out-of-scope threats

**Statement**: Nation-state, physical access, insider, DDoS,
zero-day, social engineering are out of scope.

**Source**: `Chapter12_SecurityandAudit.md §12.2.4`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Should

#### 16.3 Authentication Security

##### REQ-SEC-020: password storage

**Statement**: bcrypt rounds 12, automatic salt, hashed_password
column, HTTPS in production, never logged, min 8 / max 72 chars.

**Source**: `Chapter12_SecurityandAudit.md §12.3.1`

**Verification**: Read `password.py`; read security notes.

**Priority**: Must

##### REQ-SEC-021: JWT security

**Statement**: HS256 fixed, algorithms fixed in decode call,
alg=none rejected, expiry 24h, audience and issuer validated, type
validated, secret from env, localStorage documented trade-off.

**Source**: `Chapter12_SecurityandAudit.md §12.3.2`

**Verification**: Read `jwt.py`; run JWT tests.

**Priority**: Must

##### REQ-SEC-022: authentication failure codes

**Statement**: All auth failures map to specific codes:
UNAUTHORIZED, TOKEN_INVALID, TOKEN_EXPIRED, USER_INACTIVE,
INVALID_CREDENTIALS. Nonexistent email returns same code as wrong
password.

**Source**: `Chapter12_SecurityandAudit.md §12.3.3`

**Verification**: Read error codes; run auth tests.

**Priority**: Must

##### REQ-SEC-023: timing attack mitigation

**Statement**: `authenticate_user` runs a dummy bcrypt verification
when the user does not exist.

**Source**: `Chapter12_SecurityandAudit.md §12.3.4`

**Verification**: Read `auth_service.py`.

**Priority**: Must

#### 16.4 Authorization Security

##### REQ-SEC-030: user isolation in queries

**Statement**: Every expense and budget query filters by user_id;
every category query filters by `user_id IS NULL OR user_id =
current_user.id`.

**Source**: `Chapter12_SecurityandAudit.md §12.4.1`

**Verification**: Read service code.

**Priority**: Must

##### REQ-SEC-031: cross-user 404

**Statement**: Cross-user access returns 404, not 403, to avoid
revealing existence.

**Source**: `Chapter12_SecurityandAudit.md §12.4.2`

**Verification**: Run isolation tests.

**Priority**: Must

##### REQ-SEC-032: category access validation

**Statement**: `validate_category_access` checks system or user
ownership and returns 404 on failure.

**Source**: `Chapter12_SecurityandAudit.md §12.4.3`

**Verification**: Read `category_service.py`.

**Priority**: Must

##### REQ-SEC-033: system category protection

**Statement**: System categories cannot be updated or deleted (404);
listing and using them is allowed.

**Source**: `Chapter12_SecurityandAudit.md §12.4.4`

**Verification**: Run category tests.

**Priority**: Must

##### REQ-SEC-034: isolation test coverage

**Statement**: `test_isolation.py` verifies read, update, delete
return 404 for cross-user; list shows only own; budget isolation.

**Source**: `Chapter12_SecurityandAudit.md §12.4.5`

**Verification**: Read `test_isolation.py`.

**Priority**: Must

#### 16.5 Input Validation

##### REQ-SEC-040: Pydantic schemas

**Statement**: All request bodies validated by Pydantic v2 schemas
with strict constraints.

**Source**: `Chapter12_SecurityandAudit.md §12.5.1`

**Verification**: Read `schemas/`.

**Priority**: Must

##### REQ-SEC-041: validation rules

**Statement**: Validation rules for email, username, password,
amount, category_id, date, note, year_month, page, page_size,
months, weeks, limit, color.

**Source**: `Chapter12_SecurityandAudit.md §12.5.2`

**Verification**: Read schemas.

**Priority**: Must

##### REQ-SEC-042: SQL injection prevention

**Statement**: All database access uses SQLAlchemy ORM with
parameterized queries; no raw SQL in application code.

**Source**: `Chapter12_SecurityandAudit.md §12.5.3`

**Verification**: Search for raw SQL in `backend/app/`.

**Priority**: Must

##### REQ-SEC-043: XSS prevention

**Statement**: React escaping, no `dangerouslySetInnerHTML`, no
third-party scripts; CSP not configured in MVP (documented).

**Source**: `Chapter12_SecurityandAudit.md §12.5.4`

**Verification**: Search frontend for
`dangerouslySetInnerHTML`.

**Priority**: Must

##### REQ-SEC-044: CORS

**Statement**: CORS configured with explicit `allow_origins` from
settings; in production only the Render URL.

**Source**: `Chapter12_SecurityandAudit.md §12.5.5`

**Verification**: Read `main.py` and `render.yaml`.

**Priority**: Must

#### 16.6 Data Integrity

##### REQ-SEC-050: amount precision across layers

**Statement**: Database NUMERIC(12,2), Python Decimal, Pydantic
condecimal, JSON string, frontend string, audit string.

**Source**: `Chapter12_SecurityandAudit.md §12.6.1`

**Verification**: Read models, schemas, utils.

**Priority**: Must

##### REQ-SEC-051: date handling

**Statement**: Expense date DATE no timezone; created_at and
updated_at TIMESTAMPTZ UTC; year_month CHAR(7) no timezone.

**Source**: `Chapter12_SecurityandAudit.md §12.6.2`

**Verification**: Read models.

**Priority**: Must

##### REQ-SEC-052: database constraints

**Statement**: UNIQUE on email, username, (user_id, year_month);
CHECK on color, system consistency, amount > 0, currency = 'USD',
year_month format, action, entity_type.

**Source**: `Chapter12_SecurityandAudit.md §12.6.3`

**Verification**: Read models; inspect migration.

**Priority**: Must

#### 16.7 Audit Logging

##### REQ-SEC-060: audit design

**Statement**: Triggered by expense and budget create/update/delete;
written in the same transaction; not accessible via API; preserved
on user delete; fields: user_id, action, entity_type, entity_id,
old_value, new_value, ip_address, created_at.

**Source**: `Chapter12_SecurityandAudit.md §12.7.1`

**Verification**: Read `audit/logger.py` and service code.

**Priority**: Must

##### REQ-SEC-061: what is logged

**Statement**: CREATE has null old_value and full new_value; UPDATE
has both; DELETE has full old_value and null new_value.

**Source**: `Chapter12_SecurityandAudit.md §12.7.2`

**Verification**: Run audit tests.

**Priority**: Must

##### REQ-SEC-062: what is not logged

**Statement**: Login attempts (application logs only), registration,
read operations, category operations, failed operations are not
audited.

**Source**: `Chapter12_SecurityandAudit.md §12.7.3`

**Verification**: Inspect `audit_logs` after operations.

**Priority**: Must

##### REQ-SEC-063: audit example

**Statement**: Example audit log entry is documented with all
fields.

**Source**: `Chapter12_SecurityandAudit.md §12.7.4`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Should

##### REQ-SEC-064: audit atomicity

**Statement**: If audit write fails, the transaction is rolled
back; no business operation occurs without an audit entry.

**Source**: `Chapter12_SecurityandAudit.md §12.7.5`

**Verification**: Read service code.

**Priority**: Must

#### 16.8 Security Scan Artifacts

##### REQ-SEC-070: scan tools

**Statement**: gitleaks, semgrep, trivy, pip-audit, npm audit are
used, each writing to `security/`.

**Source**: `Chapter12_SecurityandAudit.md §12.8.1`

**Verification**: List `security/`.

**Priority**: Must

##### REQ-SEC-071: scan commands

**Statement**: Documented commands run each scan and write to the
corresponding file.

**Source**: `Chapter12_SecurityandAudit.md §12.8.2`

**Verification**: Read `Makefile` and `security/`.

**Priority**: Must

##### REQ-SEC-072: scan timing

**Statement**: Scans run after auth, after CRUD, after dashboard,
before deployment, and after final changes; results committed.

**Source**: `Chapter12_SecurityandAudit.md §12.8.3`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-SEC-073: expected findings

**Statement**: Expected findings documented: `.env.example`
placeholders (gitleaks), subprocess in MCP (semgrep), low-severity
base image CVEs (trivy), python-jose CVE (pip-audit), dev
dependency findings (npm audit).

**Source**: `Chapter12_SecurityandAudit.md §12.8.4`

**Verification**: Read scan reports.

**Priority**: Should

##### REQ-SEC-074: accepted findings

**Statement**: Any unfixed finding is documented in
`security/agent-security-notes.md` with finding, reason, mitigation,
plan.

**Source**: `Chapter12_SecurityandAudit.md §12.8.5`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

#### 16.9 PR Audit

##### REQ-SEC-080: PR audit purpose

**Statement**: `security/pr-audit.md` records at least one PR
reviewed with AI assistance.

**Source**: `Chapter12_SecurityandAudit.md §12.9.1`

**Verification**: Read `security/pr-audit.md`.

**Priority**: Must

##### REQ-SEC-081: PR audit template

**Statement**: Template includes PR details, AI review output,
issues found, verification, verdict.

**Source**: `Chapter12_SecurityandAudit.md §12.9.2`

**Verification**: Read `security/pr-audit.md`.

**Priority**: Must

##### REQ-SEC-082: PR audit coverage

**Statement**: Audit covers API contract, security, tests, code
quality, error handling, documentation.

**Source**: `Chapter12_SecurityandAudit.md §12.9.3`

**Verification**: Read `security/pr-audit.md`.

**Priority**: Must

#### 16.10 Agent and Extension Security

##### REQ-SEC-090: agent threat model

**Statement**: Seven threats for agents with mitigations: cross-user
access, unauthorized modification, backend bypass, prompt injection,
secret leakage, arbitrary code, invalid data.

**Source**: `Chapter12_SecurityandAudit.md §12.10.1`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-091: agent security controls

**Statement**: JWT auth, backend-enforced authorization, hooks,
output filtering, tool restriction, context isolation, read-only
roles, audit.

**Source**: `Chapter12_SecurityandAudit.md §12.10.2`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-092: MCP security

**Statement**: JWT verification, token from env, no database
access, strict tool schemas, exception handling, no token logging.

**Source**: `Chapter12_SecurityandAudit.md §12.10.3`

**Verification**: Read `mcp-server/`.

**Priority**: Must

##### REQ-SEC-093: hook security

**Statement**: validate_amount prevents invalid amounts;
validate_ownership prevents cross-user access; both also enforced
in backend.

**Source**: `Chapter12_SecurityandAudit.md §12.10.4`

**Verification**: Read hooks; run hook tests.

**Priority**: Must

##### REQ-SEC-094: prompt injection considerations

**Statement**: User input treated as data, skills are project
files, tool output validated, no cloud calls, MCP verifies JWT.

**Source**: `Chapter12_SecurityandAudit.md §12.10.5`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-095: agent security notes document

**Statement**: `security/agent-security-notes.md` covers
architecture, auth, hooks, permissions, limitations, accepted
risks, future improvements.

**Source**: `Chapter12_SecurityandAudit.md §12.10.6`

**Verification**: Read the file.

**Priority**: Must

#### 16.11 AI Tool and Data Policy

##### REQ-SEC-100: policy summary

**Statement**: All AI processing local; no code, prompts, or
context leaves the machine; no cloud LLM APIs; no production data;
no secrets in context.

**Source**: `Chapter12_SecurityandAudit.md §12.11.1`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

##### REQ-SEC-101: data categories

**Statement**: Source code, docs, tests, seed data, OpenAPI spec are
in agent context; real user data, production database, `.env`, JWT
tokens, JWT secret are not.

**Source**: `Chapter12_SecurityandAudit.md §12.11.2`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

##### REQ-SEC-102: AI tool inventory

**Statement**: pi-agent, qwen3.8-27b, plugins; none send data
off-machine.

**Source**: `Chapter12_SecurityandAudit.md §12.11.3`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

##### REQ-SEC-103: compliance considerations

**Statement**: Data residency local, no PII, no secrets in context,
audit via session records, reproducibility via same model version,
retention of session records in repo.

**Source**: `Chapter12_SecurityandAudit.md §12.11.4`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Should

##### REQ-SEC-104: policy document content

**Statement**: The policy document contains tool inventory, data
classification, data flow diagram, permitted and forbidden uses,
review requirements, incident response.

**Source**: `Chapter12_SecurityandAudit.md §12.11.5`

**Verification**: Read `security/ai-tool-data-policy.md`.

**Priority**: Must

#### 16.12 Known Limitations

##### REQ-SEC-110: accepted limitations

**Statement**: 12 limitations documented: no rate limiting,
localStorage JWT, no refresh token, no CSP, no CSRF token, HTTP in
local dev, no secret rotation, SQLite fallback unencrypted, shared
Render tier, no WAF, audit logs not encrypted, no 2FA.

**Source**: `Chapter12_SecurityandAudit.md §12.12.1`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-111: why accepted

**Statement**: The project is a demonstration and learning artifact
appropriate for single-user deployment, non-critical data, peer
review, and educational purposes.

**Source**: `Chapter12_SecurityandAudit.md §12.12.2`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

##### REQ-SEC-112: future improvements

**Statement**: Rate limiting (high), HttpOnly cookie (high),
refresh token rotation (medium), CSP (medium), 2FA (medium),
secret rotation (medium), audit log encryption (low), WAF (low),
penetration testing (low).

**Source**: `Chapter12_SecurityandAudit.md §12.12.3`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Should

#### 16.13 Operational Security

##### REQ-SEC-120: secrets management

**Statement**: JWT_SECRET and DATABASE_URL in env vars;
RENDER_DEPLOY_HOOK in GitHub Actions secrets; manual rotation.

**Source**: `Chapter12_SecurityandAudit.md §12.13.1`

**Verification**: Read `render.yaml` and workflows.

**Priority**: Must

##### REQ-SEC-121: gitignore

**Statement**: `.gitignore` excludes .env, local env files, *.db,
*.sqlite, `__pycache__`, node_modules, dist, build, coverage,
tool caches, .DS_Store, *.log.

**Source**: `Chapter12_SecurityandAudit.md §12.13.2`

**Verification**: Read `.gitignore`.

**Priority**: Must

##### REQ-SEC-122: git history scanning

**Statement**: gitleaks scans full git history; the project starts
with a clean history.

**Source**: `Chapter12_SecurityandAudit.md §12.13.3`

**Verification**: Read `security/gitleaks-report.json`.

**Priority**: Must

##### REQ-SEC-123: environment separation

**Statement**: Local dev uses SQLite with dev secret and
localhost:5173 CORS; Compose uses PostgreSQL with dev secret;
production uses Render PostgreSQL with generated secret and Render
URL CORS.

**Source**: `Chapter12_SecurityandAudit.md §12.13.4`

**Verification**: Read `.env.example`, `docker-compose.yml`,
`render.yaml`.

**Priority**: Must

#### 16.14 Incident Response

##### REQ-SEC-130: detection

**Statement**: Failed login spikes detected via logs; cross-user
access not possible; database unavailable via health; secret leak
via gitleaks; dependency vulnerability via audits.

**Source**: `Chapter12_SecurityandAudit.md §12.14.1`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-SEC-131: response steps

**Statement**: Six steps: identify, assess, contain, eradicate,
recover, document.

**Source**: `Chapter12_SecurityandAudit.md §12.14.2`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-SEC-132: rollback

**Statement**: Bad deployment rollback via Render dashboard;
leaked secret rotate and redeploy; database compromise N/A;
dependency vulnerability update and redeploy.

**Source**: `Chapter12_SecurityandAudit.md §12.14.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

#### 16.15 Security Design Decisions

##### REQ-SEC-140: auth and token choices

**Statement**: bcrypt rounds 12; HS256; localStorage; 24-hour
expiry; no refresh token; 404 for cross-user.

**Source**: `Chapter12_SecurityandAudit.md §12.15`

**Verification**: Read security notes.

**Priority**: Must

##### REQ-SEC-141: audit choices

**Statement**: Audit write same transaction; no API access.

**Source**: `Chapter12_SecurityandAudit.md §12.15`

**Verification**: Read service code.

**Priority**: Must

##### REQ-SEC-142: secrets and scans

**Statement**: Secrets via env vars; security scans local and
committed.

**Source**: `Chapter12_SecurityandAudit.md §12.15`

**Verification**: Read `.env.example` and `security/`.

**Priority**: Must

##### REQ-SEC-143: agent security choices

**Statement**: Agent auth JWT; data access via API; hooks pure
functions; read-only analyst; AI data policy local only; known
limitations documented; future improvements listed.

**Source**: `Chapter12_SecurityandAudit.md §12.15`

**Verification**: Read `security/agent-security-notes.md`.

**Priority**: Must

---

### 17. Operations Requirements

**Source**: `requirements/Chapter13_Operations(Ops).md`

#### 17.1 Overview

##### REQ-OPS-001: Criterion mapping

**Statement**: The ops documentation covers Criterion 13
(operational diagnosis) and Criterion 10 (deployment proof).

**Source**: `Chapter13_Operations(Ops).md §13.1`

**Verification**: Read `ops/`.

**Priority**: Must

##### REQ-OPS-002: ops directory layout

**Statement**: `ops/` contains runbook.md, health-check.md,
diagnosis.md, logging.md, deployment-health.md.

**Source**: `Chapter13_Operations(Ops).md §13.1.1`

**Verification**: List `ops/`.

**Priority**: Must

##### REQ-OPS-003: purpose of each file

**Statement**: runbook (common problems), health-check (endpoint
reference), diagnosis (worked example), logging (format and events),
deployment-health (verification record).

**Source**: `Chapter13_Operations(Ops).md §13.1.2`

**Verification**: Read each file.

**Priority**: Must

#### 17.2 Health Check Endpoint

##### REQ-OPS-010: endpoint

**Statement**: `GET /api/v1/health`, no auth, used by Render,
CI/CD, UptimeRobot, and manual checks.

**Source**: `Chapter13_Operations(Ops).md §13.2.1`

**Verification**: `curl /api/v1/health`.

**Priority**: Must

##### REQ-OPS-011: response schema

**Statement**: Returns status, database, fallback_active, version.

**Source**: `Chapter13_Operations(Ops).md §13.2.2`

**Verification**: `curl /api/v1/health`.

**Priority**: Must

##### REQ-OPS-012: field meanings

**Statement**: status ok/degraded; database postgresql/sqlite;
fallback_active boolean; version semver.

**Source**: `Chapter13_Operations(Ops).md §13.2.3`

**Verification**: Read `ops/health-check.md`.

**Priority**: Must

##### REQ-OPS-013: state combinations

**Statement**: Four combinations documented: normal production,
local dev, fallback active, and the impossible case.

**Source**: `Chapter13_Operations(Ops).md §13.2.4`

**Verification**: Read `ops/health-check.md`.

**Priority**: Should

##### REQ-OPS-014: usage

**Statement**: Used by Render health check path, CI/CD verify,
UptimeRobot ping, manual status check.

**Source**: `Chapter13_Operations(Ops).md §13.2.5`

**Verification**: Read `ops/health-check.md`.

**Priority**: Must

##### REQ-OPS-015: Render configuration

**Statement**: `render.yaml` sets `healthCheckPath:
/api/v1/health`.

**Source**: `Chapter13_Operations(Ops).md §13.2.6`

**Verification**: Read `render.yaml`.

**Priority**: Must

#### 17.3 Runbook

##### REQ-OPS-020: quick reference

**Statement**: Runbook quick reference lists seven symptoms with
sections: cold start, degraded health, 503, login failures, user
data leak, deployment failure, CI failure.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-021: cold start section

**Statement**: Documents symptom, cause, diagnosis, and action for
Render cold start.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-022: degraded health section

**Statement**: Documents symptom, cause, diagnosis, and action for
degraded health (fallback active).

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-023: 503 section

**Statement**: Documents symptom, cause, diagnosis, and action for
503 DATABASE_UNAVAILABLE.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-024: login failures section

**Statement**: Documents JWT_SECRET mismatch, diagnosis, and
action.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-025: user data leak section

**Statement**: Documents missing user_id filter, diagnosis, and
action.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-026: deployment failure section

**Statement**: Documents build/migration/env diagnosis and action.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-027: CI failure section

**Statement**: Documents dependency/env/bug diagnosis and action.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-028: escalation

**Statement**: Escalation path: check diagnosis.md, logging.md,
Render logs, GitHub issues.

**Source**: `Chapter13_Operations(Ops).md §13.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

#### 17.4 Health Check Reference

##### REQ-OPS-030: health-check.md content

**Statement**: Documents endpoint, auth, response, fields, when to
use, how it is used, what it does not check.

**Source**: `Chapter13_Operations(Ops).md §13.4`

**Verification**: Read `ops/health-check.md`.

**Priority**: Must

##### REQ-OPS-031: not checked

**Statement**: Does not check database write access, external
services, disk space, memory usage.

**Source**: `Chapter13_Operations(Ops).md §13.4`

**Verification**: Read `ops/health-check.md`.

**Priority**: Should

#### 17.5 Operational Diagnosis

##### REQ-OPS-040: diagnosis.md purpose

**Statement**: `ops/diagnosis.md` is the worked example required by
Criterion 13.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Read `ops/diagnosis.md`.

**Priority**: Must

##### REQ-OPS-041: diagnosis scenario

**Statement**: Scenario: PostgreSQL unreachable at startup; app
falls back to SQLite.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Read `ops/diagnosis.md`.

**Priority**: Must

##### REQ-OPS-042: diagnosis steps

**Statement**: Steps to reproduce with Docker Compose, stop db,
restart app, observe logs.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Follow the steps.

**Priority**: Must

##### REQ-OPS-043: diagnosis expected output

**Statement**: Expected log output (WARNING + INFO) and health
response (`degraded`, `sqlite`, `fallback_active: true`) documented.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Follow the steps; compare output.

**Priority**: Must

##### REQ-OPS-044: diagnosis expected behavior

**Statement**: Feature behavior during fallback documented: all
features work, data persistence lost on restart.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Read `ops/diagnosis.md`.

**Priority**: Must

##### REQ-OPS-045: diagnosis verification

**Statement**: Verification steps include register, login, create
expense, list expenses.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Follow the steps.

**Priority**: Must

##### REQ-OPS-046: diagnosis recovery

**Statement**: Recovery: restart db, restart backend, verify health
returns `ok`, `postgresql`.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Follow the steps.

**Priority**: Must

##### REQ-OPS-047: diagnosis findings

**Statement**: Findings table: fallback triggered within 5 seconds,
no user-facing errors, all CRUD works, all charts render, data
temporary, log clarity, health accuracy.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Read `ops/diagnosis.md`.

**Priority**: Must

##### REQ-OPS-048: diagnosis lessons

**Statement**: Four lessons documented: fallback is safety net not
persistence, health must be checked, UptimeRobot would detect,
restart required to switch back.

**Source**: `Chapter13_Operations(Ops).md §13.5`

**Verification**: Read `ops/diagnosis.md`.

**Priority**: Should

#### 17.6 Logging

##### REQ-OPS-050: log format

**Statement**: JSON structured with timestamp, level, logger, event,
extra_fields, exception when applicable.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Must

##### REQ-OPS-051: log levels

**Statement**: DEBUG development only, INFO normal, WARNING
recoverable, ERROR failures, CRITICAL unused.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Must

##### REQ-OPS-052: log events

**Statement**: 17 events documented for auth, expense, budget,
category, db.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Must

##### REQ-OPS-053: never logged

**Statement**: Passwords, JWT tokens, full bodies, raw emails, DB
connection strings, secrets never logged.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Must

##### REQ-OPS-054: log destinations

**Statement**: Local stdout, Compose stdout, Render log viewer.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Must

##### REQ-OPS-055: log viewing

**Statement**: Docker Compose logs, Render dashboard, filtering for
`fallback_triggered`, `auth.login_failed`, `db.error`,
`unhandled.error`.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Should

##### REQ-OPS-056: log retention

**Statement**: Local session only; Render per free tier policy.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Should

##### REQ-OPS-057: structured field reference

**Statement**: Documents timestamp, level, logger, event,
extra_fields, exception fields.

**Source**: `Chapter13_Operations(Ops).md §13.6`

**Verification**: Read `ops/logging.md`.

**Priority**: Should

#### 17.7 Deployment Health Record

##### REQ-OPS-060: deployment-health.md purpose

**Statement**: Records deployment state after each significant
deployment.

**Source**: `Chapter13_Operations(Ops).md §13.7`

**Verification**: Read `ops/deployment-health.md`.

**Priority**: Must

##### REQ-OPS-061: initial deployment record

**Statement**: Records platform, URL, date, version, commit, health
check response, smoke test results, screenshots, cold start,
database, notes.

**Source**: `Chapter13_Operations(Ops).md §13.7`

**Verification**: Read `ops/deployment-health.md`.

**Priority**: Must

##### REQ-OPS-062: post-expiry deployment record

**Statement**: Records the state after Render PostgreSQL expires:
health returns degraded, fallback active, all features work, data
temporary.

**Source**: `Chapter13_Operations(Ops).md §13.7`

**Verification**: Read `ops/deployment-health.md`.

**Priority**: Must

#### 17.8 Diagnosis Automation

##### REQ-OPS-070: manual diagnosis commands

**Statement**: Commands to check status, response time, database,
fallback state, and API docs.

**Source**: `Chapter13_Operations(Ops).md §13.8`

**Verification**: Run the commands.

**Priority**: Should

#### 17.9 Monitoring and Alerting

##### REQ-OPS-080: monitoring

**Statement**: Render dashboard, UptimeRobot, health endpoint.

**Source**: `Chapter13_Operations(Ops).md §13.9.1`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-081: alerting

**Statement**: Service down alert via UptimeRobot email; fallback
active manual check.

**Source**: `Chapter13_Operations(Ops).md §13.9.2`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-082: not monitored

**Statement**: CPU, memory, latency, error rate, connection pool,
disk usage are not monitored in MVP.

**Source**: `Chapter13_Operations(Ops).md §13.9.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Should

##### REQ-OPS-083: future monitoring

**Statement**: Prometheus metrics, Grafana, alert on fallback, alert
on error rate, structured log export, distributed tracing.

**Source**: `Chapter13_Operations(Ops).md §13.9.4`

**Verification**: Read `ops/runbook.md`.

**Priority**: Could

#### 17.10 Backup and Recovery

##### REQ-OPS-090: backup scope

**Statement**: No automated backups; PostgreSQL lost on expiry;
SQLite lost on restart; manual export documented.

**Source**: `Chapter13_Operations(Ops).md §13.10.1`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-091: manual export

**Statement**: `pg_dump` and `sqlite3 .dump` commands documented.

**Source**: `Chapter13_Operations(Ops).md §13.10.2`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-092: recovery

**Statement**: `psql` and `sqlite3` restore commands documented.

**Source**: `Chapter13_Operations(Ops).md §13.10.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-093: why no automated backups

**Statement**: Free tier limitation, demo scope, small data, cost.

**Source**: `Chapter13_Operations(Ops).md §13.10.4`

**Verification**: Read `ops/runbook.md`.

**Priority**: Should

##### REQ-OPS-094: future backups

**Statement**: Daily automated backup, restoration test,
point-in-time recovery, cross-region replication.

**Source**: `Chapter13_Operations(Ops).md §13.10.5`

**Verification**: Read `ops/runbook.md`.

**Priority**: Could

#### 17.11 Deployment Rollback

##### REQ-OPS-100: rollback procedure

**Statement**: Render dashboard → Deploys → previous → Redeploy.

**Source**: `Chapter13_Operations(Ops).md §13.11.1`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-101: rollback triggers

**Statement**: Health check failure, smoke test failure, user-
reported broken feature, unexpected fallback.

**Source**: `Chapter13_Operations(Ops).md §13.11.2`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-102: database rollback

**Statement**: Migrations forward-only; restore from backup or
accept fallback; no automated downgrade.

**Source**: `Chapter13_Operations(Ops).md §13.11.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Should

##### REQ-OPS-103: rollback limitations

**Statement**: Manual, no automated, no database rollback, no
canary, no blue-green.

**Source**: `Chapter13_Operations(Ops).md §13.11.4`

**Verification**: Read `ops/runbook.md`.

**Priority**: Should

#### 17.12 Ops Design Decisions

##### REQ-OPS-110: health design

**Statement**: Public, no auth; fields cover key states; fallback
reported in health.

**Source**: `Chapter13_Operations(Ops).md §13.12`

**Verification**: Read `ops/health-check.md`.

**Priority**: Must

##### REQ-OPS-111: logging design

**Statement**: JSON structured; stdout destination.

**Source**: `Chapter13_Operations(Ops).md §13.12`

**Verification**: Read `ops/logging.md`.

**Priority**: Must

##### REQ-OPS-112: monitoring design

**Statement**: Render + UptimeRobot; UptimeRobot email alerts;
manual backup; Render redeploy rollback.

**Source**: `Chapter13_Operations(Ops).md §13.12`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-OPS-113: documentation design

**Statement**: Reproducible diagnosis example; deployment record as
markdown; five ops files.

**Source**: `Chapter13_Operations(Ops).md §13.12`

**Verification**: List `ops/`.

**Priority**: Must

---

## Part 8: Delivery Requirements

### 18. CI/CD and Deployment Requirements

**Source**: `requirements/Chapter14_CICDandDeployment.md`

#### 18.1 Overview

##### REQ-CICD-001: criterion mapping

**Statement**: CI/CD and deployment cover Criterion 8
(containerization), Criterion 10 (deployment), and Criterion 11
(CI/CD pipeline).

**Source**: `Chapter14_CICDandDeployment.md §14.1.1`

**Verification**: Read `.github/workflows/`, `Dockerfile`,
`docker-compose.yml`, and `render.yaml`.

**Priority**: Must

##### REQ-CICD-002: pipeline overview

**Statement**: Pipeline: push → PR (ci.yml) → merge to main
(e2e.yml) → deploy.yml → production.

**Source**: `Chapter14_CICDandDeployment.md §14.1.2`

**Verification**: Read `.github/workflows/`.

**Priority**: Must

#### 18.2 GitHub Actions Workflows

##### REQ-CICD-010: workflow directory

**Statement**: `.github/workflows/` contains ci.yml, e2e.yml, and
deploy.yml.

**Source**: `Chapter14_CICDandDeployment.md §14.2.1`

**Verification**: List `.github/workflows/`.

**Priority**: Must

##### REQ-CICD-011: ci.yml jobs

**Statement**: ci.yml runs backend-test and frontend-test in
parallel, then compose-build; backend runs uv sync, ruff, mypy,
pytest unit and integration, coverage; frontend runs npm ci, lint,
typecheck, tests, coverage.

**Source**: `Chapter14_CICDandDeployment.md §14.2.2`

**Verification**: Read `ci.yml`.

**Priority**: Must

##### REQ-CICD-012: e2e.yml jobs

**Statement**: e2e.yml runs on push to main only; builds Docker
Compose, waits for health, installs Playwright, runs E2E tests,
uploads report on failure, stops stack.

**Source**: `Chapter14_CICDandDeployment.md §14.2.3`

**Verification**: Read `e2e.yml`.

**Priority**: Must

##### REQ-CICD-013: deploy.yml jobs

**Statement**: deploy.yml triggers after e2e.yml success; calls
Render deploy hook; waits; verifies health endpoint with retries;
reports success.

**Source**: `Chapter14_CICDandDeployment.md §14.2.4`

**Verification**: Read `deploy.yml`.

**Priority**: Must

##### REQ-CICD-014: workflow triggers summary

**Statement**: ci.yml on PR and push to main (~5 min); e2e.yml on
push to main (~8 min); deploy.yml after e2e.yml success (~2 min).

**Source**: `Chapter14_CICDandDeployment.md §14.2.5`

**Verification**: Read workflow triggers.

**Priority**: Must

##### REQ-CICD-015: no E2E on PR

**Statement**: E2E is not run on PRs to keep feedback fast and save
CI minutes.

**Source**: `Chapter14_CICDandDeployment.md §14.2.6`

**Verification**: Read `ci.yml` and `e2e.yml`.

**Priority**: Should

##### REQ-CICD-016: concurrency control

**Statement**: ci.yml and e2e.yml use `concurrency` to cancel
in-progress runs.

**Source**: `Chapter14_CICDandDeployment.md §14.2.7`

**Verification**: Read workflows.

**Priority**: Must

##### REQ-CICD-017: caching

**Statement**: Workflows cache uv dependencies, npm dependencies
(frontend and e2e), and Playwright browsers.

**Source**: `Chapter14_CICDandDeployment.md §14.2.8`

**Verification**: Read workflows.

**Priority**: Should

#### 18.3 Containerization

##### REQ-CICD-020: multi-stage Dockerfile

**Statement**: Dockerfile uses two stages: Node 20 alpine builds
the frontend; Python 3.12 slim installs uv, backend deps, backend
code, alembic, and copies the built frontend into `static/`.

**Source**: `Chapter14_CICDandDeployment.md §14.3.1`

**Verification**: Read `Dockerfile`.

**Priority**: Must

##### REQ-CICD-021: non-root user

**Statement**: The container runs as a non-root user.

**Source**: `Chapter14_CICDandDeployment.md §14.3.1`

**Verification**: Read `Dockerfile`.

**Priority**: Must

##### REQ-CICD-022: Dockerfile design decisions

**Statement**: Multi-stage, alpine for Node, slim for Python, uv
for deps, non-root user, static files copied, no dev dependencies,
pinned base image versions.

**Source**: `Chapter14_CICDandDeployment.md §14.3.2`

**Verification**: Read `Dockerfile`.

**Priority**: Must

##### REQ-CICD-023: docker-compose.yml services

**Statement**: Compose defines `db` (postgres:16-alpine with
healthcheck and named volume) and `app` (build from Dockerfile,
depends on db healthy, environment variables, port 8000,
healthcheck).

**Source**: `Chapter14_CICDandDeployment.md §14.3.3`

**Verification**: Read `docker-compose.yml`.

**Priority**: Must

##### REQ-CICD-024: compose design decisions

**Statement**: Two services; PostgreSQL 16; healthcheck on db;
healthcheck on app; named volume; single app container; explicit
CORS.

**Source**: `Chapter14_CICDandDeployment.md §14.3.4`

**Verification**: Read `docker-compose.yml`.

**Priority**: Must

##### REQ-CICD-025: development vs production

**Statement**: Development uses Vite dev server, uvicorn reload,
PostgreSQL in Compose, two containers; production uses static
files served by FastAPI, single container plus managed database.

**Source**: `Chapter14_CICDandDeployment.md §14.3.5`

**Verification**: Read docs.

**Priority**: Must

##### REQ-CICD-026: local development modes

**Statement**: Mode A (full Docker): `docker compose up --build`;
Mode B (hybrid): Compose db + local backend + local frontend.

**Source**: `Chapter14_CICDandDeployment.md §14.3.6`

**Verification**: Read `README.md`.

**Priority**: Must

#### 18.4 Render Deployment

##### REQ-CICD-030: why Render

**Statement**: No credit card, free PostgreSQL, Docker support,
health checks, GitHub integration, free SSL.

**Source**: `Chapter14_CICDandDeployment.md §14.4.1`

**Verification**: Read `README.md`.

**Priority**: Must

##### REQ-CICD-031: render.yaml

**Statement**: `render.yaml` defines a web service (Docker, free
plan, health check path, env vars) and a free PostgreSQL database.

**Source**: `Chapter14_CICDandDeployment.md §14.4.2`

**Verification**: Read `render.yaml`.

**Priority**: Must

##### REQ-CICD-032: environment variables on Render

**Statement**: DATABASE_URL from database; JWT_SECRET generated;
JWT_ALGORITHM HS256; expiry 1440; issuer and audience set;
CORS_ORIGINS Render URL; ENVIRONMENT production; APP_VERSION 1.0.0.

**Source**: `Chapter14_CICDandDeployment.md §14.4.3`

**Verification**: Read `render.yaml`.

**Priority**: Must

##### REQ-CICD-033: free tier limits

**Statement**: 512 MB RAM, 0.1 CPU, 15-minute idle sleep, 750
hours/month, 1 GB PostgreSQL, 30-day expiry, 5 GB bandwidth, 500
build minutes, 2 custom domains, no SSH.

**Source**: `Chapter14_CICDandDeployment.md §14.4.4`

**Verification**: Read `README.md` and `ops/runbook.md`.

**Priority**: Should

##### REQ-CICD-034: deployment flow

**Statement**: 10 steps: push → ci → e2e → deploy hook → Render
build → migrations → container start → Render health check →
GitHub health verify → complete.

**Source**: `Chapter14_CICDandDeployment.md §14.4.5`

**Verification**: Read workflows and `render.yaml`.

**Priority**: Must

##### REQ-CICD-035: migration in deployment

**Statement**: Migrations run in the container CMD before uvicorn
starts.

**Source**: `Chapter14_CICDandDeployment.md §14.4.6`

**Verification**: Read `Dockerfile` CMD.

**Priority**: Must

##### REQ-CICD-036: first deployment steps

**Statement**: Create Render account, new Blueprint, Render reads
render.yaml, wait for deploy, verify health, configure UptimeRobot.

**Source**: `Chapter14_CICDandDeployment.md §14.4.7`

**Verification**: Read `README.md`.

**Priority**: Must

##### REQ-CICD-037: subsequent deployments

**Statement**: Pushes to main trigger the pipeline automatically.

**Source**: `Chapter14_CICDandDeployment.md §14.4.8`

**Verification**: Read workflows.

**Priority**: Must

#### 18.5 Cold Start Mitigation

##### REQ-CICD-040: cold start problem

**Statement**: Render free tier sleeps after 15 minutes idle; next
request takes 30-60 seconds.

**Source**: `Chapter14_CICDandDeployment.md §14.5.1`

**Verification**: Read `README.md` and `ops/runbook.md`.

**Priority**: Should

##### REQ-CICD-041: UptimeRobot mitigation

**Statement**: UptimeRobot pings health endpoint every 10 minutes;
alert via email on down; expected 200.

**Source**: `Chapter14_CICDandDeployment.md §14.5.2`

**Verification**: Read `README.md`.

**Priority**: Must

##### REQ-CICD-042: README notice

**Statement**: README includes a note about free tier cold start
and UptimeRobot.

**Source**: `Chapter14_CICDandDeployment.md §14.5.3`

**Verification**: Read `README.md`.

**Priority**: Must

##### REQ-CICD-043: peer review consideration

**Statement**: Peer reviewers are asked to open the URL early and
wait for the first load.

**Source**: `Chapter14_CICDandDeployment.md §14.5.4`

**Verification**: Read `README.md`.

**Priority**: Should

#### 18.6 Rollback

##### REQ-CICD-050: rollback procedure

**Statement**: Render dashboard → service → deploys → previous
deploy → Redeploy.

**Source**: `Chapter14_CICDandDeployment.md §14.6.1`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-CICD-051: rollback triggers

**Statement**: Health check failure, E2E smoke test failure,
user-reported broken feature, unexpected fallback.

**Source**: `Chapter14_CICDandDeployment.md §14.6.2`

**Verification**: Read `ops/runbook.md`.

**Priority**: Must

##### REQ-CICD-052: database rollback

**Statement**: Forward-only migrations; revert code and write a new
migration; no `alembic downgrade` in production.

**Source**: `Chapter14_CICDandDeployment.md §14.6.3`

**Verification**: Read `ops/runbook.md`.

**Priority**: Should

##### REQ-CICD-053: rollback limitations

**Statement**: Manual, no automated, no canary, no blue-green,
brief downtime.

**Source**: `Chapter14_CICDandDeployment.md §14.6.4`

**Verification**: Read `ops/runbook.md`.

**Priority**: Should

#### 18.7 Deployment Verification

##### REQ-CICD-060: automatic verification

**Statement**: deploy.yml verifies health endpoint; workflow fails
if health fails.

**Source**: `Chapter14_CICDandDeployment.md §14.7.1`

**Verification**: Read `deploy.yml`.

**Priority**: Must

##### REQ-CICD-061: manual verification

**Statement**: Smoke test: open URL, register, add expense, set
budget, verify five charts, switch month, logout.

**Source**: `Chapter14_CICDandDeployment.md §14.7.2`

**Verification**: Read `ops/deployment-health.md`.

**Priority**: Must

##### REQ-CICD-062: verification record

**Statement**: Each deployment records date, commit, health
response, smoke test results, screenshots, notes.

**Source**: `Chapter14_CICDandDeployment.md §14.7.3`

**Verification**: Read `ops/deployment-health.md`.

**Priority**: Must

#### 18.8 Security in CI/CD

##### REQ-CICD-070: secrets

**Statement**: RENDER_DEPLOY_HOOK in GitHub Actions secrets;
JWT_SECRET and DATABASE_URL in Render env; no secrets in repo.

**Source**: `Chapter14_CICDandDeployment.md §14.8.1`

**Verification**: Search repo for secrets; read workflows.

**Priority**: Must

##### REQ-CICD-071: permissions

**Statement**: Workflows use default GITHUB_TOKEN with minimal
permissions; no long-lived AWS credentials.

**Source**: `Chapter14_CICDandDeployment.md §14.8.2`

**Verification**: Read workflows.

**Priority**: Must

##### REQ-CICD-072: supply chain

**Statement**: Pinned action versions, locked dependencies,
Dependabot not enabled (documented), Trivy run locally.

**Source**: `Chapter14_CICDandDeployment.md §14.8.3`

**Verification**: Read workflows and `security/`.

**Priority**: Should

##### REQ-CICD-073: not in CI

**Statement**: Security scans are not in CI; they run locally and
results are committed.

**Source**: `Chapter14_CICDandDeployment.md §14.8.4`

**Verification**: Read workflows and `security/`.

**Priority**: Must

#### 18.9 CI/CD Design Decisions

##### REQ-CICD-080: CI provider and split

**Statement**: GitHub Actions; backend and frontend in parallel;
integration in ci.yml; E2E only on main.

**Source**: `Chapter14_CICDandDeployment.md §14.9`

**Verification**: Read workflows.

**Priority**: Must

##### REQ-CICD-081: deploy method

**Statement**: Render deploy hook after E2E passes; health
verification post-deploy; migrations in container CMD.

**Source**: `Chapter14_CICDandDeployment.md §14.9`

**Verification**: Read workflows and `Dockerfile`.

**Priority**: Must

##### REQ-CICD-082: container and rollback choices

**Statement**: Single app container; pinned base images; non-root
user; UptimeRobot for cold start; manual Render rollback.

**Source**: `Chapter14_CICDandDeployment.md §14.9`

**Verification**: Read `Dockerfile` and `README.md`.

**Priority**: Must

##### REQ-CICD-083: security choices

**Statement**: Security scans local only; secrets in GitHub and
Render env, never in repo.

**Source**: `Chapter14_CICDandDeployment.md §14.9`

**Verification**: Read workflows and `security/`.

**Priority**: Must

---

### 19. Documentation Requirements

**Source**: `requirements/Chapter15_Documentation.md`

#### 19.1 Overview

##### REQ-DOC-001: documentation principles

**Statement**: English only; one purpose per file; reviewer-first;
living documents; linked not duplicated; short where possible.

**Source**: `Chapter15_Documentation.md §15.1.1`

**Verification**: Read the docs.

**Priority**: Must

##### REQ-DOC-002: documentation map

**Statement**: Root documents (README, product-spec, AGENTS, CLAUDE,
openapi, LICENSE); docs/; security/; ops/; screenshots/.

**Source**: `Chapter15_Documentation.md §15.1.2`

**Verification**: List each directory.

**Priority**: Must

#### 19.2 Root-Level Documents

##### REQ-DOC-010: README.md

**Statement**: README is the reviewer entry point, under 500 lines,
with sections: title, live demo, features, tech stack, architecture,
quick start, tests, API docs, AI workflow, agent pack, security,
ops, criteria mapping, project structure, license.

**Source**: `Chapter15_Documentation.md §15.2.1`

**Verification**: Read `README.md`; count lines.

**Priority**: Must

##### REQ-DOC-011: product-spec.md

**Statement**: product-spec contains problem statement, target
users, user stories, functional and non-functional requirements,
edge cases, success criteria, scope boundaries.

**Source**: `Chapter15_Documentation.md §15.2.2`

**Verification**: Read `product-spec.md`.

**Priority**: Must

##### REQ-DOC-012: AGENTS.md

**Statement**: AGENTS.md is under 60 lines, containing commands,
rules, and document links.

**Source**: `Chapter15_Documentation.md §15.2.3`

**Verification**: Read `AGENTS.md`.

**Priority**: Must

##### REQ-DOC-013: CLAUDE.md

**Statement**: CLAUDE.md is a single line `@AGENTS.md`.

**Source**: `Chapter15_Documentation.md §15.2.4`

**Verification**: Read `CLAUDE.md`.

**Priority**: Must

##### REQ-DOC-014: openapi.yaml

**Statement**: openapi.yaml is the full OpenAPI 3.1 specification.

**Source**: `Chapter15_Documentation.md §15.2.5`

**Verification**: Read `openapi.yaml`.

**Priority**: Must

##### REQ-DOC-015: LICENSE

**Statement**: LICENSE contains the MIT license text.

**Source**: `Chapter15_Documentation.md §15.2.6`

**Verification**: Read `LICENSE`.

**Priority**: Must

#### 19.3 docs/ Documents

##### REQ-DOC-020: docs/architecture.md

**Statement**: architecture.md covers overview, diagram, frontend,
backend, database, auth, directory structure, cross-cutting
concerns, and decisions.

**Source**: `Chapter15_Documentation.md §15.3.1`

**Verification**: Read `docs/architecture.md`.

**Priority**: Must

##### REQ-DOC-021: docs/api.md

**Statement**: api.md covers base URL, authentication, common
patterns, endpoint reference, examples, error codes.

**Source**: `Chapter15_Documentation.md §15.3.2`

**Verification**: Read `docs/api.md`.

**Priority**: Must

##### REQ-DOC-022: docs/process.md

**Statement**: process.md contains roles, orchestrator, lifecycle,
rules.

**Source**: `Chapter15_Documentation.md §15.3.3`

**Verification**: Read `docs/process.md`.

**Priority**: Must

##### REQ-DOC-023: docs/ai-workflow.md

**Statement**: ai-workflow.md contains tools, workflow, context
engineering, roles, orchestration, example prompts, session records,
correction log, skills, subagents, MCP tools, review, and data
policy.

**Source**: `Chapter15_Documentation.md §15.3.4`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-DOC-024: docs/design-system.md

**Statement**: design-system.md contains colors, typography,
spacing, components, chart colors, states, and accessibility.

**Source**: `Chapter15_Documentation.md §15.3.5`

**Verification**: Read `docs/design-system.md`.

**Priority**: Must

##### REQ-DOC-025: docs/testing-guidelines.md

**Statement**: testing-guidelines.md contains test layers, backend
rules, frontend rules, E2E rules, coverage policy, naming, and what
not to test.

**Source**: `Chapter15_Documentation.md §15.3.6`

**Verification**: Read `docs/testing-guidelines.md`.

**Priority**: Must

##### REQ-DOC-026: docs/agent-extension-pack.md

**Statement**: agent-extension-pack.md contains overview, skills,
hooks, MCP server, subagents, permissions, and design principles.

**Source**: `Chapter15_Documentation.md §15.3.7`

**Verification**: Read `docs/agent-extension-pack.md`.

**Priority**: Must

##### REQ-DOC-027: docs/permissions.md

**Statement**: permissions.md contains user roles, resource
permissions, agent permissions, skill permissions, subagent
permissions, enforcement, forbidden actions, and escalation.

**Source**: `Chapter15_Documentation.md §15.3.8`

**Verification**: Read `docs/permissions.md`.

**Priority**: Must

##### REQ-DOC-028: docs/task-template.md

**Statement**: task-template.md contains the four grooming sections:
Goal, Acceptance criteria, Out of scope, Constraints.

**Source**: `Chapter15_Documentation.md §15.3.9`

**Verification**: Read `docs/task-template.md`.

**Priority**: Must

##### REQ-DOC-029: docs/team/*.md

**Statement**: team/ contains pm.md, software-engineer.md, and
qa-engineer.md with role definitions.

**Source**: `Chapter15_Documentation.md §15.3.10–9.3.12`

**Verification**: List `docs/team/`.

**Priority**: Must

#### 19.4 security/ Documents

##### REQ-DOC-030: security/ contents

**Statement**: security/ contains pr-audit.md,
gitleaks-report.json, semgrep-report.json, trivy-report.json,
pip-audit-report.txt, npm-audit-report.txt,
agent-security-notes.md, ai-tool-data-policy.md.

**Source**: `Chapter15_Documentation.md §15.4`

**Verification**: List `security/`.

**Priority**: Must

#### 19.5 ops/ Documents

##### REQ-DOC-031: ops/ contents

**Statement**: ops/ contains runbook.md, health-check.md,
diagnosis.md, logging.md, deployment-health.md.

**Source**: `Chapter15_Documentation.md §15.5`

**Verification**: List `ops/`.

**Priority**: Must

#### 19.6 Screenshots

##### REQ-DOC-040: screenshots directory

**Statement**: screenshots/ contains dashboard.png,
expense-form.png, budget-page.png, health-check.png.

**Source**: `Chapter15_Documentation.md §15.6`

**Verification**: List `screenshots/`.

**Priority**: Must

##### REQ-DOC-041: screenshot guidelines

**Statement**: Consistent viewport, realistic data, no real
personal data, < 500 KB each.

**Source**: `Chapter15_Documentation.md §15.6.4`

**Verification**: Inspect screenshots.

**Priority**: Should

#### 19.7 Environment and Makefile

##### REQ-DOC-050: .env.example

**Statement**: .env.example lists all environment variables with
placeholders; the real `.env` is gitignored; no real secrets.

**Source**: `Chapter15_Documentation.md §15.7`

**Verification**: Read `.env.example`; run gitleaks.

**Priority**: Must

##### REQ-DOC-051: Makefile targets

**Statement**: Makefile targets: dev, down, test, test-backend,
test-frontend, e2e, lint, migrate, seed, security.

**Source**: `Chapter15_Documentation.md §15.8`

**Verification**: Read `Makefile`.

**Priority**: Must

#### 19.8 Documentation Guidelines

##### REQ-DOC-060: writing rules

**Statement**: English only, present tense, active voice, short
paragraphs, tables for comparisons, code blocks for commands, no
marketing language, no emojis, no screenshots in docs/.

**Source**: `Chapter15_Documentation.md §15.9.1`

**Verification**: Read the docs.

**Priority**: Should

##### REQ-DOC-061: linking rules

**Statement**: Link, do not duplicate; relative links; descriptive
link text; every document linked from somewhere.

**Source**: `Chapter15_Documentation.md §15.9.2`

**Verification**: Search for orphan documents.

**Priority**: Should

##### REQ-DOC-062: updating rules

**Statement**: Corrections update the relevant document; new
decisions update architecture or process; new skill updates the
pack; new permission updates permissions; new error code updates
api.md and openapi.yaml.

**Source**: `Chapter15_Documentation.md §15.9.3`

**Verification**: Read `docs/ai-workflow.md` correction log.

**Priority**: Must

##### REQ-DOC-063: document ownership

**Statement**: Ownership table exists for each document.

**Source**: `Chapter15_Documentation.md §15.9.4`

**Verification**: Read `Chapter15_Documentation.md`.

**Priority**: Should

#### 19.9 Reviewer Quick Path

##### REQ-DOC-070: 5-minute live verification

**Statement**: Steps: open live URL, register, add expense, set
budget, verify five charts, switch month, log out.

**Source**: `Chapter15_Documentation.md §15.10.1`

**Verification**: Follow the steps.

**Priority**: Must

##### REQ-DOC-071: 5-minute local verification

**Statement**: Clone, cp .env.example, docker compose up --build,
open localhost:8000, repeat live steps.

**Source**: `Chapter15_Documentation.md §15.10.2`

**Verification**: Follow the steps.

**Priority**: Must

##### REQ-DOC-072: evidence checklist

**Statement**: Table maps each of the 14 criteria to a specific
file to open.

**Source**: `Chapter15_Documentation.md §15.10.3`

**Verification**: Use the checklist.

**Priority**: Must

#### 19.10 Documentation Design Decisions

##### REQ-DOC-080: language and layout

**Statement**: English only; minimal root docs; details in docs/;
README < 500 lines; AGENTS.md < 60 lines.

**Source**: `Chapter15_Documentation.md §15.11`

**Verification**: Read README and AGENTS.md.

**Priority**: Must

##### REQ-DOC-081: criteria mapping location

**Statement**: Criteria mapping is in README so reviewers find
evidence fast.

**Source**: `Chapter15_Documentation.md §15.11`

**Verification**: Read `README.md`.

**Priority**: Must

##### REQ-DOC-082: screenshots location

**Statement**: Screenshots live in `screenshots/`, not in docs/ or
root.

**Source**: `Chapter15_Documentation.md §15.11`

**Verification**: List directories.

**Priority**: Must

##### REQ-DOC-083: no extra files

**Statement**: No peer-review-guide.md (merged into README); no
CHANGELOG (git history); no CONTRIBUTING; no CODE_OF_CONDUCT.

**Source**: `Chapter15_Documentation.md §15.11`

**Verification**: List repository root.

**Priority**: Should

##### REQ-DOC-084: API docs strategy

**Statement**: openapi.yaml plus FastAPI's /docs and /redoc
provide contract and interactive view.

**Source**: `Chapter15_Documentation.md §15.11`

**Verification**: Open `/docs` on the running app.

**Priority**: Must

##### REQ-DOC-085: diagrams and formatting

**Statement**: ASCII diagrams in markdown; fenced code blocks with
language; tables for comparisons; no emojis.

**Source**: `Chapter15_Documentation.md §15.11`

**Verification**: Read the docs.

**Priority**: Should

---

### 20. Project Structure Requirements

**Source**: `requirements/Chapter16_ProjectStructure.md`

#### 20.1 Repository Tree

##### REQ-STRUCT-001: complete repository tree

**Statement**: The repository tree matches the structure documented
in Chapter 16, including root files, `.github/`, `frontend/`,
`backend/`, `e2e/`, `docs/`, `security/`, `ops/`,
`agent-capabilities/`, `agent-hooks/`, `mcp-server/`,
`custom-agent/`, `.agents/`, and `screenshots/`.

**Source**: `Chapter16_ProjectStructure.md §16.1`

**Verification**: List the repository recursively; compare.

**Priority**: Must

#### 20.2 Directory Responsibilities

##### REQ-STRUCT-010: top-level directory responsibilities

**Statement**: Each top-level directory has a defined
responsibility and owner.

**Source**: `Chapter16_ProjectStructure.md §16.2.1`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-011: frontend subdirectory responsibilities

**Statement**: Each `frontend/src/` subdirectory has a defined
responsibility.

**Source**: `Chapter16_ProjectStructure.md §16.2.2`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-012: backend subdirectory responsibilities

**Statement**: Each `backend/app/` subdirectory has a defined
responsibility.

**Source**: `Chapter16_ProjectStructure.md §16.2.3`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

#### 20.3 File Purpose Reference

##### REQ-STRUCT-020: root file purposes

**Statement**: Each root file has a defined purpose and, where
applicable, a mapped criterion.

**Source**: `Chapter16_ProjectStructure.md §16.3.1`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-021: workflow file purposes

**Statement**: Each workflow file has a defined purpose and mapped
criterion.

**Source**: `Chapter16_ProjectStructure.md §16.3.2`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-022: frontend file purposes

**Statement**: Each frontend file has a defined purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.3`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-023: backend file purposes

**Statement**: Each backend file has a defined purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.4`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-024: E2E file purposes

**Statement**: Each E2E file has a defined purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.5`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-025: docs file purposes

**Statement**: Each docs file has a defined purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.6`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-026: security file purposes

**Statement**: Each security file has a defined purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.7`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-027: ops file purposes

**Statement**: Each ops file has a defined purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.8`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-028: agent extension file purposes

**Statement**: Each agent extension file has a defined purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.9`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Must

##### REQ-STRUCT-029: symlink purposes

**Statement**: Each symlink has a defined target and purpose.

**Source**: `Chapter16_ProjectStructure.md §16.3.10`

**Verification**: `ls -la .agents/`.

**Priority**: Must

#### 20.4 File Count

##### REQ-STRUCT-040: file count summary

**Statement**: The project totals approximately 230 files across
root, CI/CD, frontend, backend, E2E, docs, security, ops, agent
extension, and screenshots.

**Source**: `Chapter16_ProjectStructure.md §16.4`

**Verification**: Count files.

**Priority**: Should

#### 20.5 Naming Conventions

##### REQ-STRUCT-050: file naming

**Statement**: React components PascalCase.tsx; hooks camelCase.ts
with `use` prefix; TypeScript modules camelCase.ts; test files
same name + `.test.ts(x)`; Python modules snake_case.py; Python
tests `test_` prefix; Markdown kebab-case.md; JSON reports
kebab-case.json; migrations NNN_description.py.

**Source**: `Chapter16_ProjectStructure.md §16.5.1`

**Verification**: List files; compare names.

**Priority**: Must

##### REQ-STRUCT-051: directory naming

**Statement**: Feature directories lowercase; Python packages
snake_case; agent tool directories kebab-case; docs subdirectories
lowercase.

**Source**: `Chapter16_ProjectStructure.md §16.5.2`

**Verification**: List directories.

**Priority**: Must

##### REQ-STRUCT-052: mixed conventions rationale

**Statement**: Python follows PEP 8; React follows community
convention; Markdown uses kebab-case for URLs; agent tools match
tool conventions.

**Source**: `Chapter16_ProjectStructure.md §16.5.3`

**Verification**: Read `Chapter16_ProjectStructure.md`.

**Priority**: Should

#### 20.6 Excluded Files

##### REQ-STRUCT-060: excluded content

**Statement**: `.env`, node_modules, .venv, `__pycache__`, *.db,
dist, build, coverage, tool caches, .DS_Store, *.log, real user
data, production dumps, RENDER_DEPLOY_HOOK are excluded.

**Source**: `Chapter16_ProjectStructure.md §16.6`

**Verification**: Read `.gitignore`; search repo.

**Priority**: Must

#### 20.7 Structure Design Decisions

##### REQ-STRUCT-070: monorepo choice

**Statement**: Single repository with top-level frontend, backend,
e2e, docs, security, ops, and agent directories.

**Source**: `Chapter16_ProjectStructure.md §16.7`

**Verification**: List repository root.

**Priority**: Must

##### REQ-STRUCT-071: agent directories choice

**Statement**: Agent capabilities, hooks, MCP, and custom-agent
live in their own top-level directories with symlinks in
`.agents/`.

**Source**: `Chapter16_ProjectStructure.md §16.7`

**Verification**: List those directories.

**Priority**: Must

##### REQ-STRUCT-072: tests beside code

**Statement**: Frontend tests use `*.test.ts(x)` beside source;
backend tests separate in `tests/unit/` and `tests/integration/`.

**Source**: `Chapter16_ProjectStructure.md §16.7`

**Verification**: List test files.

**Priority**: Must

##### REQ-STRUCT-073: no extra tooling

**Statement**: No `src/` at root; no Turborepo or Nx; flat layout.

**Source**: `Chapter16_ProjectStructure.md §16.7`

**Verification**: List root.

**Priority**: Should

---

### 21. Development Plan Requirements

**Source**: `requirements/Chapter17DevelopmentPlan.md`

#### 21.1 Phase Summary

##### REQ-PLAN-001: eight phases

**Statement**: The project is built in eight phases: spec and
skeleton, authentication, core CRUD, dashboard, container and CI/CD,
agent extension pack, security and ops, docs and polish.

**Source**: `Chapter17DevelopmentPlan.md §17.1.1`

**Verification**: Read `docs/ai-workflow.md`; read the plan.

**Priority**: Must

##### REQ-PLAN-002: phase dependencies

**Statement**: Phases are sequential; Phase 4 and Phase 5 may run in
parallel.

**Source**: `Chapter17DevelopmentPlan.md §17.1.2`

**Verification**: Read the plan.

**Priority**: Should

#### 21.2 Phase 1: Spec and Skeleton

##### REQ-PLAN-010: phase 1 tasks

**Statement**: 17 tasks: write product-spec, create repo structure,
write AGENTS.md, CLAUDE.md, process.md, three role files,
task-template.md, create ~30 issues, groom all issues, initialize
backend and frontend with passing tests, write `.env.example`,
`.gitignore`, LICENSE, Makefile.

**Source**: `Chapter17DevelopmentPlan.md §17.2.2`

**Verification**: Read the plan; inspect repo.

**Priority**: Must

##### REQ-PLAN-011: phase 1 deliverables

**Statement**: product-spec.md, AGENTS.md, CLAUDE.md, process.md,
team/, task-template.md, repo skeleton, groomed backlog, backend and
frontend skeletons, root config files.

**Source**: `Chapter17DevelopmentPlan.md §17.2.3`

**Verification**: List repository.

**Priority**: Must

##### REQ-PLAN-012: phase 1 verification

**Statement**: Spec complete; backend starts; frontend starts;
issues groomed; agent can read context.

**Source**: `Chapter17DevelopmentPlan.md §17.2.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.3 Phase 2: Authentication

##### REQ-PLAN-020: phase 2 tasks

**Statement**: 15 tasks: user model, password, JWT, register, login,
me, auth dependency, auth unit tests, auth integration tests,
AuthContext, axios client, login page, register page, ProtectedRoute,
frontend auth tests.

**Source**: `Chapter17DevelopmentPlan.md §17.3.2`

**Verification**: Read the plan; inspect code.

**Priority**: Must

##### REQ-PLAN-021: phase 2 verification

**Statement**: Register, login, token, duplicate email, wrong
password, frontend login, frontend redirect, tests pass.

**Source**: `Chapter17DevelopmentPlan.md §17.3.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.4 Phase 3: Core CRUD

##### REQ-PLAN-030: phase 3 tasks

**Statement**: 25 tasks covering categories, expenses, budgets,
audit, isolation tests, and frontend pages.

**Source**: `Chapter17DevelopmentPlan.md §17.4.2`

**Verification**: Read the plan; inspect code.

**Priority**: Must

##### REQ-PLAN-031: phase 3 verification

**Statement**: CRUD tests pass; audit logged; user isolation
verified; frontend works; Decimal precision holds.

**Source**: `Chapter17DevelopmentPlan.md §17.4.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.5 Phase 4: Dashboard

##### REQ-PLAN-040: phase 4 tasks

**Statement**: 19 tasks covering six dashboard endpoints, chart
components, MonthContext, MonthPicker, KPI cards, chart tests, and
integration tests.

**Source**: `Chapter17DevelopmentPlan.md §17.5.2`

**Verification**: Read the plan; inspect code.

**Priority**: Must

##### REQ-PLAN-041: phase 4 verification

**Statement**: Summary correct; category breakdown sum equals
total; trend includes empty months; cumulative last point equals
total; heatmap has seven days per week; recent limit respected;
month switch updates all; charts render.

**Source**: `Chapter17DevelopmentPlan.md §17.5.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.6 Phase 5: Container and CI/CD

##### REQ-PLAN-050: phase 5 tasks

**Statement**: 15 tasks: Dockerfile, Compose, health check, SQLite
fallback, render.yaml, three workflows, Playwright setup, three
E2E specs, first deploy, UptimeRobot, deployment-health.md.

**Source**: `Chapter17DevelopmentPlan.md §17.6.2`

**Verification**: Read the plan; inspect code.

**Priority**: Must

##### REQ-PLAN-051: phase 5 verification

**Statement**: Docker build works; full stack runs; CI passes; E2E
passes; deploy works; health endpoint works; README has cold start
note; UptimeRobot active.

**Source**: `Chapter17DevelopmentPlan.md §17.6.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.7 Phase 6: Agent Extension Pack

##### REQ-PLAN-060: phase 6 tasks

**Statement**: 20 tasks: three skills, two hooks, hook README, MCP
server, auth, four tools, MCP README, two subagents, symlinks, two
docs, hook tests, manual MCP test.

**Source**: `Chapter17DevelopmentPlan.md §17.7.2`

**Verification**: Read the plan; inspect code.

**Priority**: Must

##### REQ-PLAN-061: phase 6 verification

**Statement**: Skills discoverable; hooks importable; hook tests
pass; MCP server starts; MCP tools work; subagents defined;
permissions documented.

**Source**: `Chapter17DevelopmentPlan.md §17.7.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.8 Phase 7: Security and Ops

##### REQ-PLAN-070: phase 7 tasks

**Statement**: 13 tasks: run gitleaks, semgrep, trivy, pip-audit,
npm audit; write pr-audit, agent-security-notes, ai-tool-data-policy,
runbook, health-check, diagnosis, logging, deployment-health.

**Source**: `Chapter17DevelopmentPlan.md §17.8.2`

**Verification**: Read the plan; inspect files.

**Priority**: Must

##### REQ-PLAN-071: phase 7 verification

**Statement**: All scan files exist; no real secrets found;
diagnosis reproducible; runbook covers common issues; deployment
record accurate.

**Source**: `Chapter17DevelopmentPlan.md §17.8.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.9 Phase 8: Docs and Polish

##### REQ-PLAN-080: phase 8 tasks

**Statement**: 13 tasks: write README, architecture.md, api.md,
design-system.md, testing-guidelines.md, ai-workflow.md; capture
screenshots; run final tests; deploy; verify live; update
deployment-health; criteria mapping check; peer review dry run.

**Source**: `Chapter17DevelopmentPlan.md §17.9.2`

**Verification**: Read the plan; inspect files.

**Priority**: Must

##### REQ-PLAN-081: phase 8 verification

**Statement**: README under 500 lines; all docs present;
screenshots exist; all tests pass; live URL works; criteria mapped.

**Source**: `Chapter17DevelopmentPlan.md §17.9.4`

**Verification**: Run each check.

**Priority**: Must

#### 21.10 Milestones

##### REQ-PLAN-090: milestones

**Statement**: Eight milestones M1–M8 aligned with the eight phases,
each with a criteria statement.

**Source**: `Chapter17DevelopmentPlan.md §17.10`

**Verification**: Read the plan.

**Priority**: Must

#### 21.11 Risk Register

##### REQ-PLAN-100: technical risks

**Statement**: Ten technical risks documented with probability,
impact, and mitigation: Render PostgreSQL expiry, cold start,
pi-agent struggles, context limit, MCP failure, E2E flaky, scan
false positives, dashboard overrun, SQLite/PostgreSQL differences,
Decimal handling bug.

**Source**: `Chapter17DevelopmentPlan.md §17.11.1`

**Verification**: Read the plan.

**Priority**: Must

##### REQ-PLAN-101: process risks

**Statement**: Seven process risks: spec vague, spec detailed, AI
wrong code, review skipped, issues too large, correction not
written, session records incomplete.

**Source**: `Chapter17DevelopmentPlan.md §17.11.2`

**Verification**: Read the plan.

**Priority**: Should

##### REQ-PLAN-102: scope risks

**Statement**: Six scope risks: feature creep, extra charts,
multi-currency, shared budgets, mobile, dark mode.

**Source**: `Chapter17DevelopmentPlan.md §17.11.3`

**Verification**: Read the plan.

**Priority**: Should

##### REQ-PLAN-103: deployment risks

**Statement**: Six deployment risks: deploy failure, migration
failure, cold start, bandwidth, build minutes, secret leak.

**Source**: `Chapter17DevelopmentPlan.md §17.11.4`

**Verification**: Read the plan.

**Priority**: Should

#### 21.12 Daily Workflow

##### REQ-PLAN-110: daily workflow

**Statement**: Nine-step daily workflow: pick issue, groom, implement,
verify, fix on FAIL, close on PASS, commit, CI runs, update session
records.

**Source**: `Chapter17DevelopmentPlan.md §17.12`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

##### REQ-PLAN-111: time allocation

**Statement**: Writing code 40%, reviewing AI output 20%, grooming
10%, testing 15%, docs 10%, debugging 5%.

**Source**: `Chapter17DevelopmentPlan.md §17.12.1`

**Verification**: Read the plan.

**Priority**: Should

##### REQ-PLAN-112: session discipline

**Statement**: One issue per session, fresh session for QA, commit
after each issue, update docs after corrections, record sessions.

**Source**: `Chapter17DevelopmentPlan.md §17.12.2`

**Verification**: Read `docs/ai-workflow.md`.

**Priority**: Must

#### 21.13 Development Plan Design Decisions

##### REQ-PLAN-120: phase structure

**Statement**: Eight phases, sequential with Phase 4 and 5 parallel-
izable, estimated 25 days.

**Source**: `Chapter17DevelopmentPlan.md §17.13`

**Verification**: Read the plan.

**Priority**: Must

##### REQ-PLAN-121: workflow and discipline

**Statement**: PM → SWE → QA loop; one issue per session;
documentation throughout; screenshots in Phase 8; security scans in
Phase 7; peer review dry run in Phase 8.

**Source**: `Chapter17DevelopmentPlan.md §17.13`

**Verification**: Read `docs/process.md`.

**Priority**: Must

---

## Part 9: Acceptance and Mapping

### 22. Final Project Criteria Mapping

**Source**: `requirements/Chapter1_ProjectOverview.md §1.5`,
`requirements/Chapter15_Documentation.md §15.10.3`

#### 22.1 Criteria to Requirement Mapping

| Criterion | Requirements | Evidence Location |
|---|---|---|
| 1. Problem Description | REQ-PROJ-001 to REQ-PROJ-009, REQ-PROD-001 to REQ-PROD-007 | `README.md`, `product-spec.md` |
| 2. AI-Assisted Development Workflow | REQ-AI-001 to REQ-AI-143 | `AGENTS.md`, `docs/ai-workflow.md`, `docs/process.md`, `docs/team/` |
| 3. Technologies and System Architecture | REQ-TECH-001 to REQ-TECH-091, REQ-ARCH-001 to REQ-ARCH-082 | `docs/architecture.md`, `frontend/`, `backend/` |
| 4. Frontend Implementation | REQ-FE-001 to REQ-FE-144 | `frontend/`, frontend tests, `docs/design-system.md` |
| 5. API Contract | REQ-API-001 to REQ-API-114 | `openapi.yaml` |
| 6. Backend Implementation | REQ-BE-001 to REQ-BE-152 | `backend/`, `backend/tests/` |
| 7. Database Integration | REQ-DB-001 to REQ-DB-135 | `backend/alembic/`, `backend/app/models/`, `docs/architecture.md` |
| 8. Containerization | REQ-TECH-040 to REQ-TECH-042, REQ-CICD-020 to REQ-CICD-026 | `Dockerfile`, `docker-compose.yml` |
| 9. Integration Testing | REQ-TEST-020 to REQ-TEST-045 | `e2e/`, `backend/tests/integration/` |
| 10. Deployment | REQ-CICD-030 to REQ-CICD-062, REQ-OPS-060 to REQ-OPS-062 | Live URL, `render.yaml`, `ops/deployment-health.md` |
| 11. CI/CD Pipeline | REQ-CICD-010 to REQ-CICD-017, REQ-CICD-080 to REQ-CICD-083 | `.github/workflows/` |
| 12. Agent Extension Pack | REQ-AI-060 to REQ-AI-143, REQ-EXT-001 to REQ-EXT-083 | `agent-capabilities/`, `agent-hooks/`, `mcp-server/`, `custom-agent/`, `docs/agent-extension-pack.md`, `docs/permissions.md` |
| 13. Security, Audit, DevOps Hardening | REQ-SEC-001 to REQ-SEC-143, REQ-OPS-001 to REQ-OPS-113 | `security/`, `ops/` |
| 14. Reproducibility | REQ-PROJ-009, REQ-DOC-010, REQ-DOC-050, REQ-DOC-051, REQ-DOC-070 to REQ-DOC-072 | `README.md`, `Makefile`, `.env.example` |

#### 22.2 Criterion 1: Problem Description

**Requirement**: The README clearly describes the problem, the system
functionality, and expected behavior.

**Evidence**:
- `README.md` top section
- `product-spec.md §2.1` (problem statement)
- `product-spec.md §2.2` (user stories)
- `product-spec.md §2.3` (functional requirements)

**Verification**: Read README and product-spec; confirm the problem
and expected behavior are clear.

#### 22.3 Criterion 2: AI-Assisted Development Workflow

**Requirement**: The project clearly documents the AI workflow,
including prompts or task delegation, context files, manual review,
and verification.

**Evidence**:
- `AGENTS.md` (context)
- `docs/ai-workflow.md` (workflow, real sessions, correction log)
- `docs/process.md` (orchestration, roles)
- `docs/team/pm.md`, `docs/team/software-engineer.md`,
  `docs/team/qa-engineer.md` (role definitions)

**Verification**: Read `docs/ai-workflow.md`; confirm real sessions
with dates, prompts, agent output, human review, and commit hashes.

#### 22.4 Criterion 3: Technologies and System Architecture

**Requirement**: The project clearly describes the frontend, backend,
database, containerization, CI/CD, and how they fit together.

**Evidence**:
- `docs/architecture.md`
- `frontend/package.json`
- `backend/pyproject.toml`
- `docker-compose.yml`
- `.github/workflows/`

**Verification**: Read `docs/architecture.md`; confirm diagrams and
technology choices with rationale.

#### 22.5 Criterion 4: Frontend Implementation

**Requirement**: The frontend is functional, well structured, and
includes tests covering core logic, with clear instructions for
running them.

**Evidence**:
- `frontend/src/` (structure)
- `frontend/src/api/` (centralized API layer)
- `frontend/src/components/charts/` (five charts)
- `frontend/src/**/*.test.ts(x)` (tests)
- `make test-frontend`
- `docs/design-system.md`

**Verification**: Run `make test-frontend`; inspect `src/api/`;
confirm five charts exist.

#### 22.6 Criterion 5: API Contract

**Requirement**: The OpenAPI specification reflects frontend
requirements and is used as the contract for backend development.

**Evidence**:
- `openapi.yaml`
- `frontend/src/api/` (maps to OpenAPI endpoints)
- `backend/app/routers/` (implements OpenAPI endpoints)
- Integration tests assert response shapes match schemas

**Verification**: Compare `openapi.yaml` with FastAPI `/openapi.json`;
run integration tests.

#### 22.7 Criterion 6: Backend Implementation

**Requirement**: The backend is well structured, follows the OpenAPI
specification, and includes tests covering core functionality.

**Evidence**:
- `backend/app/` (layered structure)
- `backend/tests/unit/` (unit tests)
- `backend/tests/integration/` (integration tests)
- `make test-backend`

**Verification**: Run `make test-backend`; inspect layer separation;
confirm endpoints match `openapi.yaml`.

#### 22.8 Criterion 7: Database Integration

**Requirement**: The database layer is properly integrated, supports
different environments, and is documented.

**Evidence**:
- `backend/app/models/` (SQLAlchemy models)
- `backend/alembic/` (migrations)
- `backend/app/database.py` (engine selection, fallback)
- `docker-compose.yml` (PostgreSQL for Compose)
- `render.yaml` (PostgreSQL for production)
- `.env.example` (DATABASE_URL)
- `docs/architecture.md`

**Verification**: Confirm models, migrations, and environment
configuration; test fallback via `ops/diagnosis.md`.

#### 22.9 Criterion 8: Containerization

**Requirement**: The full system runs via Docker or Docker Compose
with clear instructions.

**Evidence**:
- `Dockerfile` (multi-stage build)
- `docker-compose.yml` (app + db)
- `README.md` (quick start)
- `Makefile` (`make dev`)

**Verification**: `docker compose up --build`; open
`http://localhost:8000`.

#### 22.10 Criterion 9: Integration Testing

**Requirement**: Integration tests are clearly separated, cover key
workflows, and are documented.

**Evidence**:
- `backend/tests/integration/`
- `e2e/tests/` (three specs)
- `e2e/playwright.config.ts`
- `docs/testing-guidelines.md`
- `make e2e`

**Verification**: Run `make e2e`; confirm tests cover registration,
expense CRUD, budget, dashboard, isolation, and month switch.

#### 22.11 Criterion 10: Deployment

**Requirement**: The application is deployed to the cloud with a
working URL or clear proof of deployment.

**Evidence**:
- Live URL
- `render.yaml`
- `ops/deployment-health.md` (deployment record with health check
  and smoke test results)
- `screenshots/health-check.png`

**Verification**: Open the live URL; confirm the app works; read
`ops/deployment-health.md`.

#### 22.12 Criterion 11: CI/CD Pipeline

**Requirement**: The CI/CD pipeline runs tests and deploys the
application when tests pass.

**Evidence**:
- `.github/workflows/ci.yml` (PR tests)
- `.github/workflows/e2e.yml` (main branch E2E)
- `.github/workflows/deploy.yml` (deploy after E2E passes)
- `security/pr-audit.md`

**Verification**: Inspect workflows; confirm the deploy workflow
verifies health after deployment.

#### 22.13 Criterion 12: Agent Extension Pack

**Requirement**: The project includes a documented extension pack
with project instructions, a reusable workflow, a subagent/
specialist, an MCP tool/server, a hook or guardrail, and permission
notes.

**Evidence**:
- `AGENTS.md` (project instructions)
- `docs/process.md` (reusable workflow)
- `custom-agent/finance-analyst.md`, `custom-agent/qa-reviewer.md`
  (subagents)
- `mcp-server/` (MCP server with four tools)
- `agent-hooks/validate-amount.py`,
  `agent-hooks/validate-ownership.py` (hooks)
- `docs/permissions.md` (permission notes)
- `docs/agent-extension-pack.md` (overview)
- `agent-capabilities/` (three skills)

**Verification**: List each directory; run hook tests; start MCP
server; read `docs/agent-extension-pack.md`.

#### 22.14 Criterion 13: Security, Audit, DevOps Hardening

**Requirement**: The project includes PR audit output, deterministic
security scan findings, agent/extension security notes, operational
diagnosis output, and an AI tool/data policy.

**Evidence**:
- `security/pr-audit.md` (PR audit)
- `security/gitleaks-report.json` (secret scan)
- `security/semgrep-report.json` (SAST)
- `security/trivy-report.json` (dependency scan)
- `security/pip-audit-report.txt`
- `security/npm-audit-report.txt`
- `security/agent-security-notes.md`
- `security/ai-tool-data-policy.md`
- `ops/diagnosis.md` (operational diagnosis)
- `ops/runbook.md`, `ops/health-check.md`, `ops/logging.md`
- `ops/deployment-health.md`

**Verification**: List `security/` and `ops/`; read
`ops/diagnosis.md`; follow the steps to reproduce.

#### 22.15 Criterion 14: Reproducibility

**Requirement**: Clear instructions exist to set up, run, test, and
deploy the system end to end.

**Evidence**:
- `README.md` Quick Start (Docker and hybrid modes)
- `Makefile` (all common commands)
- `.env.example` (environment template)
- `render.yaml` (deployment config)
- `docs/api.md` (API usage)
- `ops/runbook.md` (troubleshooting)

**Verification**: Follow the README Quick Start; run `make test`
and `make e2e`; deploy to Render.

---

### 23. Requirements Traceability Matrix

#### 23.1 How to Use

Each requirement ID maps to:
- The source chapter and section
- Its domain
- Its priority
- Its verification method

Use this matrix to check that all requirements are covered and that
each one has a verification path.

#### 23.2 Domain Summary

| Domain | Requirement Range | Count | Source Chapter |
|---|---|---|---|
| PROJ | REQ-PROJ-001 to REQ-PROJ-009 | 9 | Chapter 1 |
| PROD | REQ-PROD-001 to REQ-PROD-043 | 43 | Chapter 2 |
| TECH | REQ-TECH-001 to REQ-TECH-091 | 91 | Chapter 3 |
| ARCH | REQ-ARCH-001 to REQ-ARCH-082 | 82 | Chapter 4 |
| DB | REQ-DB-001 to REQ-DB-135 | 135 | Chapter 5 |
| BE | REQ-BE-001 to REQ-BE-152 | 152 | Chapter 6 |
| API | REQ-API-001 to REQ-API-114 | 114 | Chapter 7 |
| FE | REQ-FE-001 to REQ-FE-144 | 144 | Chapter 8 |
| AI | REQ-AI-001 to REQ-AI-143 | 143 | Chapter 9 |
| EXT | REQ-EXT-001 to REQ-EXT-083 | 83 | Chapter 10 |
| TEST | REQ-TEST-001 to REQ-TEST-082 | 82 | Chapter 11 |
| SEC | REQ-SEC-001 to REQ-SEC-143 | 143 | Chapter 12 |
| OPS | REQ-OPS-001 to REQ-OPS-113 | 113 | Chapter 13 |
| CICD | REQ-CICD-001 to REQ-CICD-083 | 83 | Chapter 14 |
| DOC | REQ-DOC-001 to REQ-DOC-085 | 85 | Chapter 15 |
| STRUCT | REQ-STRUCT-001 to REQ-STRUCT-073 | 73 | Chapter 16 |
| PLAN | REQ-PLAN-001 to REQ-PLAN-121 | 121 | Chapter 17 |

**Total requirements**: approximately 1,566.

#### 23.3 Priority Summary

| Priority | Meaning | Count (approximate) |
|---|---|---|
| Must | Required for completion | ~1,200 |
| Should | Strongly recommended | ~300 |
| Could | Optional improvement | ~66 |

#### 23.4 Traceability Format

For each requirement, the traceability is:

```
REQ-<DOMAIN>-<NNN>
  → Source: requirements/ChapterX_Name.md §X.Y.Z
  → Verification: <how to verify>
  → Priority: Must / Should / Could
```

#### 23.5 Cross-Domain Dependencies

| Requirement | Depends On |
|---|---|
| REQ-API-040 (GET /expenses) | REQ-BE-071 (list_expenses service) |
| REQ-BE-070 (create_expense) | REQ-DB-030 (expenses table) |
| REQ-FE-062 (DashboardPage) | REQ-API-060 to REQ-API-065 (dashboard endpoints) |
| REQ-EXT-034 (add_expense tool) | REQ-BE-070 (create_expense service) |
| REQ-SEC-030 (user isolation) | REQ-BE-070 to REQ-BE-074 (service methods) |
| REQ-CICD-011 (ci.yml) | REQ-TEST-050 (Makefile targets) |
| REQ-OPS-040 (diagnosis.md) | REQ-BE-130 (engine selection) |
| REQ-PLAN-050 (Phase 5) | REQ-TECH-040 to REQ-TECH-042 (containerization) |

---

### 24. Acceptance Checklist

#### 24.1 Functional Acceptance

| # | Check | Requirement | How to Verify |
|---|---|---|---|
| 1 | User can register | REQ-PROD-010, REQ-API-020 | Register in the app |
| 2 | User can log in | REQ-PROD-010, REQ-API-021 | Log in |
| 3 | User can view profile | REQ-PROD-010, REQ-API-022 | Visit `/auth/me` |
| 4 | User can create expense | REQ-PROD-011, REQ-API-041 | Add an expense |
| 5 | User can list expenses | REQ-PROD-011, REQ-API-040 | View expense list |
| 6 | User can filter by month | REQ-PROD-011 | Use the month picker |
| 7 | User can filter by category | REQ-PROD-011 | Use the category filter |
| 8 | User can update expense | REQ-PROD-011, REQ-API-043 | Edit an expense |
| 9 | User can delete expense | REQ-PROD-011, REQ-API-044 | Delete an expense |
| 10 | User can set monthly budget | REQ-PROD-012, REQ-API-051 | Set a budget |
| 11 | User can update budget | REQ-PROD-012 | Change the budget |
| 12 | User can delete budget | REQ-PROD-012, REQ-API-052 | Delete the budget |
| 13 | User can view budget status | REQ-PROD-012, REQ-API-050 | Check budget page |
| 14 | User can see system categories | REQ-PROD-013, REQ-API-030 | Open categories page |
| 15 | User can create custom category | REQ-PROD-013, REQ-API-031 | Add a category |
| 16 | User cannot modify system categories | REQ-PROD-013 | Confirm no edit/delete on system |
| 17 | Dashboard KPI cards render | REQ-PROD-014, REQ-FE-062 | View dashboard |
| 18 | Category pie chart renders | REQ-PROD-014, REQ-FE-070 | View dashboard |
| 19 | Monthly trend bar chart renders | REQ-PROD-014, REQ-FE-071 | View dashboard |
| 20 | Cumulative line chart renders | REQ-PROD-014, REQ-FE-072 | View dashboard |
| 21 | Line turns red when over budget | REQ-PROD-014 | Exceed budget |
| 22 | Weekly heatmap renders | REQ-PROD-014, REQ-FE-073 | View dashboard |
| 23 | Recent transactions list renders | REQ-PROD-014 | View dashboard |
| 24 | Budget progress bar renders | REQ-PROD-014, REQ-FE-074 | View dashboard |
| 25 | Month switch updates all charts | REQ-PROD-014 | Use month picker |
| 26 | Empty states shown | REQ-PROD-014, REQ-FE-101 | Use with no data |
| 27 | Audit log records writes | REQ-PROD-015, REQ-SEC-060 | Inspect DB |
| 28 | Audit log not exposed via API | REQ-PROD-015 | Confirm no audit router |
| 29 | Health endpoint works | REQ-PROD-016, REQ-OPS-010 | `curl /api/v1/health` |
| 30 | SQLite fallback works | REQ-PROD-017, REQ-BE-130 | Follow `ops/diagnosis.md` |
| 31 | User A cannot see User B's data | REQ-PROD-010, REQ-SEC-030 | Run isolation tests |
| 32 | All five charts visible | REQ-PROJ-004 | View dashboard |
| 33 | System categories always available | REQ-PROD-013 | Confirm on fresh account |
| 34 | Custom categories usable | REQ-PROD-013 | Create expense with custom category |

#### 24.2 Technical Acceptance

| # | Check | Requirement | How to Verify |
|---|---|---|---|
| 1 | Backend unit tests pass | REQ-TEST-010 to REQ-TEST-018 | `make test-backend-unit` |
| 2 | Backend integration tests pass | REQ-TEST-020 to REQ-TEST-026 | `make test-backend-integration` |
| 3 | Frontend tests pass | REQ-TEST-030 to REQ-TEST-039 | `make test-frontend` |
| 4 | E2E tests pass | REQ-TEST-040 to REQ-TEST-045 | `make e2e` |
| 5 | Docker Compose runs full stack | REQ-CICD-023 | `docker compose up --build` |
| 6 | Dockerfile builds | REQ-CICD-020 | `docker build -t app .` |
| 7 | CI runs on PR | REQ-CICD-011 | Open a test PR |
| 8 | E2E runs on main | REQ-CICD-012 | Push to main |
| 9 | Deploy runs after E2E | REQ-CICD-013 | Merge to main |
| 10 | Health check passes post-deploy | REQ-CICD-060 | Read workflow output |
| 11 | Cold start under 60 seconds | REQ-PROD-020 | Open live URL after idle |
| 12 | Health reports correct state | REQ-OPS-011 | `curl /api/v1/health` |
| 13 | SQLite fallback triggered within 5s | REQ-PROD-017 | Follow `ops/diagnosis.md` |
| 14 | Decimal precision holds | REQ-DB-090 | Run Decimal tests |
| 15 | User isolation verified by tests | REQ-SEC-034 | Run `test_isolation.py` |
| 16 | CI/CD pipeline complete | REQ-CICD-002 | Read workflows |
| 17 | Render deployment succeeds | REQ-CICD-036 | Read `ops/deployment-health.md` |
| 18 | Migrations run in container | REQ-CICD-035 | Read `Dockerfile` CMD |
| 19 | No real secrets in repo | REQ-SEC-071 | Run gitleaks |
| 20 | All scan artifacts present | REQ-SEC-070 | List `security/` |

#### 24.3 Quality Acceptance

| # | Check | Requirement | How to Verify |
|---|---|---|---|
| 1 | README under 500 lines | REQ-DOC-010 | `wc -l README.md` |
| 2 | All docs present | REQ-DOC-002 | List `docs/` |
| 3 | Screenshots present | REQ-DOC-040 | List `screenshots/` |
| 4 | Criteria mapping present | REQ-PROJ-005, REQ-DOC-081 | Read README |
| 5 | AI workflow documented with real sessions | REQ-AI-110 to REQ-AI-113 | Read `docs/ai-workflow.md` |
| 6 | Correction log present | REQ-AI-120 to REQ-AI-122 | Read `docs/ai-workflow.md` |
| 7 | Agent Extension Pack functional | REQ-EXT-001 to REQ-EXT-083 | Verify each component |
| 8 | Hook tests pass | REQ-EXT-072 | `pytest test_agent_hooks.py` |
| 9 | Permissions documented | REQ-EXT-060 | Read `docs/permissions.md` |
| 10 | Security artifacts present | REQ-SEC-001 | List `security/` |
| 11 | Ops artifacts present | REQ-OPS-002 | List `ops/` |
| 12 | Diagnosis reproducible | REQ-OPS-042 | Follow `ops/diagnosis.md` |
| 13 | Deployment record present | REQ-OPS-060 | Read `ops/deployment-health.md` |
| 14 | Peer reviewer can reproduce in < 10 min | REQ-PROJ-009, REQ-DOC-071 | Follow README Quick Start |
| 15 | README 5-minute verification path | REQ-DOC-070 | Follow the path |

#### 24.4 Measurable Targets

| # | Metric | Target | Requirement | How to Verify |
|---|---|---|---|---|
| 1 | Backend test count | >= 50 | REQ-PROD-043 | Count tests |
| 2 | Frontend test count | >= 20 | REQ-PROD-043 | Count tests |
| 3 | E2E test count | >= 3 | REQ-PROD-043 | Count specs |
| 4 | API endpoints | >= 15 | REQ-PROD-043 | Count in `openapi.yaml` |
| 5 | Dashboard charts | 5 | REQ-PROD-043 | Count in `components/charts/` |
| 6 | System categories | 10 | REQ-PROD-043 | Query DB |
| 7 | Security artifacts | 8 | REQ-PROD-043 | List `security/` |
| 8 | Ops artifacts | 5 | REQ-PROD-043 | List `ops/` |
| 9 | Agent skills | 3 | REQ-PROD-043 | List `agent-capabilities/` |
| 10 | Agent subagents | 2 | REQ-PROD-043 | List `custom-agent/` |
| 11 | MCP tools | 4 | REQ-PROD-043 | Read `mcp-server/server.py` |
| 12 | Agent hooks | 2 | REQ-PROD-043 | List `agent-hooks/` |
| 13 | Documentation files | >= 20 | REQ-PROD-043 | Count docs |
| 14 | README length | < 500 lines | REQ-PROD-043 | `wc -l README.md` |
| 15 | Setup time | < 10 minutes | REQ-PROD-043 | Time the setup |
| 16 | Cold start | < 60 seconds | REQ-PROD-043 | Time first request |

#### 24.5 Final Project Criteria Acceptance

| # | Criterion | Requirement Range | Evidence |
|---|---|---|---|
| 1 | Problem Description | REQ-PROJ-001 to REQ-PROD-007 | README, product-spec |
| 2 | AI Workflow | REQ-AI-001 to REQ-AI-143 | `docs/ai-workflow.md` |
| 3 | Architecture | REQ-TECH-001 to REQ-ARCH-082 | `docs/architecture.md` |
| 4 | Frontend | REQ-FE-001 to REQ-FE-144 | `frontend/` |
| 5 | API Contract | REQ-API-001 to REQ-API-114 | `openapi.yaml` |
| 6 | Backend | REQ-BE-001 to REQ-BE-152 | `backend/` |
| 7 | Database | REQ-DB-001 to REQ-DB-135 | `backend/alembic/` |
| 8 | Containerization | REQ-CICD-020 to REQ-CICD-026 | `Dockerfile`, Compose |
| 9 | Integration Testing | REQ-TEST-020 to REQ-TEST-045 | `e2e/`, `backend/tests/integration/` |
| 10 | Deployment | REQ-CICD-030 to REQ-CICD-062 | Live URL, `render.yaml` |
| 11 | CI/CD | REQ-CICD-010 to REQ-CICD-083 | `.github/workflows/` |
| 12 | Agent Extension Pack | REQ-EXT-001 to REQ-EXT-083 | Agent directories |
| 13 | Security/Audit/DevOps | REQ-SEC-001 to REQ-OPS-113 | `security/`, `ops/` |
| 14 | Reproducibility | REQ-PROJ-009, REQ-DOC-070 to REQ-DOC-072 | README, Makefile |

---

## Part 10: Appendices

### 25. Appendix A: Environment Variables

**Source**: `requirements/Chapter3_TechStack.md §3.10`,
`requirements/Chapter14_CICDandDeployment.md §14.4.3`

#### 25.1 Backend Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| DATABASE_URL | sqlite:///./dev.db | No (Yes in prod) | Database connection string |
| DB_CONNECT_TIMEOUT | 5 | No | Seconds to wait for PostgreSQL |
| JWT_SECRET | dev-secret-change-in-production | Yes (prod) | Signing secret |
| JWT_ALGORITHM | HS256 | No | Fixed signing algorithm |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | No | Token lifetime (24 hours) |
| JWT_ISSUER | expense-tracker | No | Token issuer claim |
| JWT_AUDIENCE | expense-tracker-api | No | Token audience claim |
| CORS_ORIGINS | ["http://localhost:5173"] | No | Allowed origins |
| ENVIRONMENT | development | No | development or production |
| APP_VERSION | 1.0.0 | No | Application version |
| LOG_LEVEL | INFO | No | Logging level |

#### 25.2 Frontend Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| VITE_API_BASE_URL | http://localhost:8000/api/v1 | No | Backend API base URL |

#### 25.3 MCP Server Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| MCP_API_BASE_URL | http://localhost:8000/api/v1 | No | Backend API base URL |
| MCP_JWT_SECRET | ${JWT_SECRET} | Yes | Same secret as backend |
| MCP_USER_TOKEN | (empty) | Yes at runtime | User access token |

#### 25.4 Render-Managed Variables

| Variable | Source | Notes |
|---|---|---|
| DATABASE_URL | Render PostgreSQL | Injected automatically |
| JWT_SECRET | Render generated | Random on first deploy |
| JWT_ALGORITHM | Static value | HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Static value | 1440 |
| JWT_ISSUER | Static value | expense-tracker |
| JWT_AUDIENCE | Static value | expense-tracker-api |
| CORS_ORIGINS | Static value | Render URL only |
| ENVIRONMENT | Static value | production |
| APP_VERSION | Static value | 1.0.0 |

#### 25.5 GitHub Actions Secrets

| Secret | Used By |
|---|---|
| RENDER_DEPLOY_HOOK | `deploy.yml` |

---

### 26. Appendix B: Error Codes

**Source**: `requirements/Chapter6_BackendDesign.md §6.12.3`,
`requirements/Chapter7_APIContract(OpenAPI).md §7.8.3`

#### 26.1 Error Code Table

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
| INTERNAL_ERROR | 500 | Unexpected error | - |

#### 26.2 Error Response Shape

```json
{
  "detail": "Human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "field": "optional_field_name"
}
```

#### 26.3 HTTP Status Usage

| Status | Meaning | Used For |
|---|---|---|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Action not allowed |
| 404 | Not Found | Resource missing or not owned |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Unexpected error |
| 503 | Service Unavailable | Database error |

---

### 27. Appendix C: API Endpoints

**Source**: `requirements/Chapter7_APIContract(OpenAPI).md`

#### 27.1 Health

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | /health | No | Health check |

#### 27.2 Auth

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | /auth/register | No | Register user |
| POST | /auth/login | No | Login and get token |
| GET | /auth/me | Yes | Current user |

#### 27.3 Categories

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | /categories | Yes | List categories |
| POST | /categories | Yes | Create custom category |
| DELETE | /categories/{category_id} | Yes | Delete custom category |

#### 27.4 Expenses

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | /expenses | Yes | List expenses |
| POST | /expenses | Yes | Create expense |
| GET | /expenses/{expense_id} | Yes | Get expense |
| PUT | /expenses/{expense_id} | Yes | Update expense |
| DELETE | /expenses/{expense_id} | Yes | Delete expense |

#### 27.5 Budgets

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | /budgets/{year_month} | Yes | Get budget |
| PUT | /budgets/{year_month} | Yes | Set/update budget |
| DELETE | /budgets/{year_month} | Yes | Delete budget |

#### 27.6 Dashboard

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | /dashboard/summary | Yes | Monthly summary |
| GET | /dashboard/by-category | Yes | Category breakdown |
| GET | /dashboard/trend | Yes | Monthly trend |
| GET | /dashboard/cumulative | Yes | Cumulative spending |
| GET | /dashboard/heatmap | Yes | Weekly heatmap |
| GET | /dashboard/recent | Yes | Recent transactions |

#### 27.7 Endpoint Count

| Group | Count |
|---|---|
| Health | 1 |
| Auth | 3 |
| Categories | 3 |
| Expenses | 5 |
| Budgets | 3 |
| Dashboard | 6 |
| **Total** | **21** |

---

### 28. Appendix D: Test Files

**Source**: `requirements/Chapter11_TestingStrategy.md`

#### 28.1 Backend Unit Tests

| File | Tests |
|---|---|
| `backend/tests/unit/test_password.py` | Hash, verify, salt |
| `backend/tests/unit/test_jwt.py` | Claims, decode, expiry, aud, iss |
| `backend/tests/unit/test_auth_service.py` | Register, login, duplicates |
| `backend/tests/unit/test_category_service.py` | List, create, delete |
| `backend/tests/unit/test_expense_service.py` | CRUD, audit, isolation |
| `backend/tests/unit/test_budget_service.py` | Upsert, get, delete, invalid |
| `backend/tests/unit/test_dashboard_service.py` | Summary, category, trend, cumulative, heatmap, recent |
| `backend/tests/unit/test_audit_logger.py` | Audit write |
| `backend/tests/unit/test_decimal_helpers.py` | Decimal conversion |

#### 28.2 Backend Integration Tests

| File | Tests |
|---|---|
| `backend/tests/integration/test_auth_api.py` | Register, login, me |
| `backend/tests/integration/test_categories_api.py` | Category endpoints |
| `backend/tests/integration/test_expenses_api.py` | Expense endpoints |
| `backend/tests/integration/test_budgets_api.py` | Budget endpoints |
| `backend/tests/integration/test_dashboard_api.py` | Dashboard endpoints |
| `backend/tests/integration/test_isolation.py` | Cross-user access |
| `backend/tests/integration/test_health_api.py` | Health endpoint |
| `backend/tests/integration/test_agent_hooks.py` | Hook behavior |

#### 28.3 Frontend Tests

| File | Tests |
|---|---|
| `frontend/src/utils/format.test.ts` | formatUSD, formatPercent, formatMonth |
| `frontend/src/utils/date.test.ts` | currentYearMonth, shiftMonth, monthRange |
| `frontend/src/utils/validation.test.ts` | amountSchema, expenseFormSchema |
| `frontend/src/components/charts/BudgetProgress.test.tsx` | Color logic, cap, no-budget |
| `frontend/src/components/charts/WeeklyHeatmap.test.tsx` | Days, colors, max-zero |
| `frontend/src/components/charts/CategoryPieChart.test.tsx` | Empty, data, merge |
| `frontend/src/components/forms/ExpenseForm.test.tsx` | Validation, cancel |
| `frontend/src/pages/LoginPage.test.tsx` | Fields, validation, errors |

#### 28.4 E2E Tests

| File | Scenario |
|---|---|
| `e2e/tests/happy-path.spec.ts` | Complete user flow |
| `e2e/tests/isolation.spec.ts` | User data isolation |
| `e2e/tests/month-switch.spec.ts` | Month switching |

#### 28.5 Test Counts

| Layer | Count (approximate) |
|---|---|
| Backend unit | 9 files, ~50 tests |
| Backend integration | 8 files, ~60 tests |
| Frontend | 8 files, ~30 tests |
| E2E | 3 files, 3 tests |

---

### 29. Appendix E: Agent Extension Pack

**Source**: `requirements/Chapter10_AgentExtensionPack.md`

#### 29.1 Skills

| Skill | Directory | Purpose |
|---|---|---|
| monthly-report | `agent-capabilities/monthly-report/SKILL.md` | Generate monthly report |
| add-expense | `agent-capabilities/add-expense/SKILL.md` | Add expense with validation |
| budget-check | `agent-capabilities/budget-check/SKILL.md` | Check budget status |

#### 29.2 Hooks

| Hook | File | Purpose |
|---|---|---|
| validate_amount | `agent-hooks/validate-amount.py` | Reject invalid amounts |
| validate_ownership | `agent-hooks/validate-ownership.py` | Reject cross-user access |

#### 29.3 MCP Server

| Component | File | Purpose |
|---|---|---|
| Entry | `mcp-server/server.py` | MCP server with tools |
| Auth | `mcp-server/auth.py` | JWT verification |
| Config | `mcp-server/config.py` | MCP settings |
| add_expense | `mcp-server/tools/add_expense.py` | Create expense |
| get_budget_status | `mcp-server/tools/get_budget_status.py` | Budget status |
| monthly_summary | `mcp-server/tools/monthly_summary.py` | Category breakdown |
| list_expenses | `mcp-server/tools/list_expenses.py` | List expenses |
| README | `mcp-server/README.md` | Documentation |

#### 29.4 Subagents

| Subagent | File | Purpose |
|---|---|---|
| finance-analyst | `custom-agent/finance-analyst.md` | Analyze spending |
| qa-reviewer | `custom-agent/qa-reviewer.md` | Verify work |

#### 29.5 Documentation

| File | Purpose |
|---|---|
| `docs/agent-extension-pack.md` | Pack overview |
| `docs/permissions.md` | Permission matrix |

#### 29.6 Symlinks

| Symlink | Target |
|---|---|
| `.agents/skills/monthly-report` | `agent-capabilities/monthly-report` |
| `.agents/skills/add-expense` | `agent-capabilities/add-expense` |
| `.agents/skills/budget-check` | `agent-capabilities/budget-check` |
| `.agents/agents/finance-analyst.md` | `custom-agent/finance-analyst.md` |
| `.agents/agents/qa-reviewer.md` | `custom-agent/qa-reviewer.md` |

---

### 30. Appendix F: Glossary and Abbreviations

#### 30.1 Terms

| Term | Definition | Source |
|---|---|---|
| API Contract | The OpenAPI specification that both frontend and backend follow | Chapter 7 |
| Agent Extension Pack | Skills, hooks, MCP server, subagents, permissions | Chapter 10 |
| Audit Log | Database record of every expense and budget write | Chapter 5 §5.7 |
| Cold Start | Delay when Render free tier wakes from idle sleep | Chapter 14 §14.5 |
| Criteria Mapping | Table mapping Final Project criteria to evidence | Chapter 15 §15.10 |
| Decimal | Exact decimal type for money values | Chapter 5 §5.11 |
| Fallback | Automatic switch to SQLite when PostgreSQL is unreachable | Chapter 5 §5.13 |
| Graph Engineering | Multi-agent workflow with specialized roles | Chapter 9 §9.5.6 |
| Hook | Guardrail that validates inputs before an action | Chapter 10 §10.3 |
| Loop Engineering | Running an agent until a stop condition | Chapter 9 §9.5.5 |
| MCP | Model Context Protocol; exposes tools to the agent | Chapter 9 §9.9 |
| MVP | Minimum Viable Product | Chapter 1 §1.6 |
| Orchestrator | Main session enforcing PM → SWE → QA | Chapter 9 §9.5 |
| PM Agent | Product Manager role that grooms issues | Chapter 9 §9.4.1 |
| QA Agent | Quality Assurance role that verifies issues | Chapter 9 §9.4.3 |
| Skill | Reusable procedure the agent can discover | Chapter 10 §10.2 |
| SQLite Fallback | See Fallback | Chapter 5 §5.13 |
| Subagent | Specialized agent with a separate context | Chapter 10 §10.5 |
| SWE Agent | Software Engineer role that implements issues | Chapter 9 §9.4.2 |
| year_month | String in YYYY-MM format used as budget key | Chapter 5 §5.6 |

#### 30.2 Abbreviations

| Abbreviation | Meaning |
|---|---|
| A11y | Accessibility |
| API | Application Programming Interface |
| CI | Continuous Integration |
| CD | Continuous Deployment |
| CORS | Cross-Origin Resource Sharing |
| CRUD | Create, Read, Update, Delete |
| CSP | Content Security Policy |
| E2E | End-to-End |
| HMR | Hot Module Replacement |
| JWT | JSON Web Token |
| MCP | Model Context Protocol |
| MSW | Mock Service Worker |
| OIDC | OpenID Connect |
| ORM | Object-Relational Mapping |
| OTel | OpenTelemetry (not used in MVP) |
| PII | Personally Identifiable Information |
| RTL | React Testing Library |
| SAST | Static Application Security Testing |
| SPA | Single Page Application |
| SSR | Server-Side Rendering |
| TTI | Time to Interactive |
| UI | User Interface |
| USD | United States Dollar |
| UX | User Experience |
| VPC | Virtual Private Cloud (out of scope) |
| WAF | Web Application Firewall (out of scope) |

#### 30.3 Chapter Reference Table

| Chapter | File | Topic |
|---|---|---|
| 1 | `requirements/Chapter1_ProjectOverview.md` | Project overview |
| 2 | `requirements/Chapter2_ProductSpecification.md` | Product specification |
| 3 | `requirements/Chapter3_TechStack.md` | Tech stack |
| 4 | `requirements/Chapter4_SystemArchitecture.md` | System architecture |
| 5 | `requirements/Chapter5_DatabaseDesign.md` | Database design |
| 6 | `requirements/Chapter6_BackendDesign.md` | Backend design |
| 7 | `requirements/Chapter7_APIContract(OpenAPI).md` | API contract |
| 8 | `requirements/Chapter8_FrontendDesign.md` | Frontend design |
| 9 | `requirements/Chapter9_AIWorkflow.md` | AI workflow |
| 10 | `requirements/Chapter10_AgentExtensionPack.md` | Agent extension pack |
| 11 | `requirements/Chapter11_TestingStrategy.md` | Testing strategy |
| 12 | `requirements/Chapter12_SecurityandAudit.md` | Security and audit |
| 13 | `requirements/Chapter13_Operations(Ops).md` | Operations |
| 14 | `requirements/Chapter14_CICDandDeployment.md` | CI/CD and deployment |
| 15 | `requirements/Chapter15_Documentation.md` | Documentation |
| 16 | `requirements/Chapter16_ProjectStructure.md` | Project structure |
| 17 | `requirements/Chapter17DevelopmentPlan.md` | Development plan |

---

## Tech stack

> **Derived index.** This section restates, without changing, the normative
> requirements of §7 (Tech Stack Requirements, REQ-TECH-001 … REQ-TECH-091).
> It exists at level 2 so that machine readers (`scripts/generate_factpack.ts`
> `extractSection`, `skills/definer/details/survey.md` input validation) can
> locate the stack in one block. Where this summary and a REQ entry differ,
> the **REQ entry wins**.

**Frontend** (REQ-TECH-001 … 010)

- React 18 + TypeScript 5, built with Vite 5 (REQ-TECH-001)
- React Router v6 — nested routes and route guards (REQ-TECH-002)
- Tailwind CSS 3, no runtime CSS-in-JS (REQ-TECH-003)
- Recharts 2 for all five chart types (REQ-TECH-004)
- TanStack Query 5 for server state — caching, retries, invalidation (REQ-TECH-005)
- React Hook Form 7 + Zod 3 for forms and validation (REQ-TECH-006)
- Axios 1 with auth/error interceptors (REQ-TECH-007)
- date-fns 3 (REQ-TECH-008, Should)
- Vitest 1 + React Testing Library 14 + MSW 2 (REQ-TECH-009)
- ESLint 8, Prettier 3, TypeScript ESLint 7 (REQ-TECH-010, Should)

**Backend** (REQ-TECH-020 … 028)

- Python 3.12 + FastAPI 0.110+ (REQ-TECH-020)
- SQLAlchemy 2.0 + Alembic 1.13+ (REQ-TECH-021)
- Pydantic 2 for request/response validation (REQ-TECH-022)
- python-jose 3.3+ (JWT) + passlib[bcrypt] 1.7+ (password hashing) (REQ-TECH-023)
- uvicorn 0.29+ ASGI server (REQ-TECH-024)
- uv for dependency management (REQ-TECH-025)
- httpx 0.27+ for tests and internal calls (REQ-TECH-026)
- pytest 8, pytest-cov 5, pytest-asyncio 0.23+ (REQ-TECH-027)
- ruff 0.4+ lint/format, mypy type checking (REQ-TECH-028)

**Database** (REQ-TECH-030 … 032)

- SQLite for local development, PostgreSQL in Docker Compose and production (REQ-TECH-030)
- All access through SQLAlchemy, no raw SQL (REQ-TECH-031)
- SQLite `PRAGMA foreign_keys = ON` per connection (REQ-TECH-032)

**Containerization** (REQ-TECH-040 … 042)

- `node:20-alpine` (frontend build), `python:3.12-slim` (backend runtime), `postgres:16-alpine` (Compose) (REQ-TECH-040)
- Compose services: `db` (PostgreSQL) + `app` (REQ-TECH-041)
- Production: single app container serving built static frontend (REQ-TECH-042)

**CI/CD and deployment** (REQ-TECH-050 … 062)

- GitHub Actions: `ci.yml`, `e2e.yml`, `deploy.yml` (REQ-TECH-050)
- Triggers: `ci.yml` on PR + push to main; `e2e.yml` on push to main (REQ-TECH-051)
- Render free tier with PostgreSQL; documented free-tier limits (REQ-TECH-060, 061)
- Cold-start mitigation: UptimeRobot pings health every 10 minutes (REQ-TECH-062)

**Development tools and AI** (REQ-TECH-070 … 091)

- pi-agent with qwen3.8-27b running locally (REQ-TECH-070)
- All code, prompts and context stay on the local machine (REQ-TECH-071)
- Git + GitHub, Conventional Commits (REQ-TECH-072)
- Quality: ruff + mypy (Python), ESLint + Prettier + tsc (TypeScript) (REQ-TECH-073)
- Security scanning: gitleaks, semgrep, trivy, pip-audit (REQ-TECH-074)
- Testing: pytest, Vitest, React Testing Library, Playwright (REQ-TECH-075)
- Monitoring: Render logs, health check endpoint (REQ-TECH-076)
- Versions pinned in `pyproject.toml`/`uv.lock`, `package.json`/lockfile, Docker tags, Actions major versions (REQ-TECH-080 … 083)
- Configuration via environment variables; `.env.example` holds placeholders only (REQ-TECH-090, 091)

## Core features

> **Derived index.** Restates the functional requirements of §6.2
> (REQ-PROD-010 … REQ-PROD-017) as a feature list for machine readers. Where
> this list and a REQ entry differ, the **REQ entry wins**. Out-of-scope items
> are listed in REQ-PROJ-007 and REQ-FE-143.

- **Authentication** — registration, login, current user, logout, with validation rules and error codes (REQ-PROD-010; FR-AUTH-1…4)
- **Expense management** — create, list, get, update, delete, with validation, per-user isolation and audit behavior (REQ-PROD-011; FR-EXP-1…5)
- **Budgets** — set (upsert), get (returns 0 if absent), delete, with audit behavior (REQ-PROD-012; FR-BUD-1…3)
- **Categories** — list, create, system-category protection (REQ-PROD-013; FR-CAT-1…3)
- **Dashboard** — summary, by-category, trend, cumulative, heatmap, recent activity, including edge cases (REQ-PROD-014; FR-DASH-1…6)
- **Audit logging** — written in the same transaction as the business operation; never exposed by any API endpoint (REQ-PROD-015; FR-AUD-1…2)
- **Health check** — public endpoint returning status, database, fallback_active, version (REQ-PROD-016; FR-HEALTH-1)
- **Database fallback** — automatic switch to SQLite within 5 seconds when PostgreSQL is unreachable at startup, with table creation and category seeding; data written during fallback is temporary (REQ-PROD-017; FR-DB-1)

---

## Document End

This document consolidates the requirements for the Expense Tracker &
Budget Dashboard project. It is intended to be used alongside the 17
chapter documents in the `requirements/` directory.

**Total parts**: 10
**Total sections**: 30
**Total requirement domains**: 17
**Total requirements**: approximately 1,566

For detailed context on any requirement, consult the source chapter
and section referenced in the requirement entry.