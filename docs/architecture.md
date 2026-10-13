# Architecture

Technical architecture of the Expense Tracker Dashboard, written against
the merged code (not against an ideal). Every file cited here exists on
`main` at the time of writing. Related documents:
[api.md](api.md), [design-system.md](design-system.md),
[testing-guidelines.md](testing-guidelines.md).

## Overview

A single-container full-stack application:

- **Frontend**: a React 18 + TypeScript single-page application (SPA)
  built with Vite and styled with Tailwind CSS. Charts are rendered with
  Recharts. The source lives in `frontend/src`.
- **Backend**: a FastAPI (Python 3.12) application with SQLAlchemy 2.0,
  Alembic migrations, Pydantic settings and JWT bearer authentication.
  The source lives in `backend/app`.
- **Database**: PostgreSQL 16 in production and in `docker-compose.yml`;
  a SQLite fallback file (`fallback.db`) keeps the app usable when the
  primary database is unreachable at startup.

The production image is built by the root `Dockerfile`, which builds the
frontend and copies the built assets into `backend/static`; the FastAPI
app then serves both the API and the SPA from one process (see
`README.md` for the run instructions and `openapi.yaml` for the API
contract).

## Diagram

```text
+---------------------------------------------------------------+
|                        Browser (SPA client)                    |
|         React 18 + Vite build, Tailwind, Recharts              |
+-------------------------------+-------------------------------+
                                | HTTPS (fetch, /api/v1/*)
                                v
+---------------------------------------------------------------+
|                     FastAPI process (port 8000)                |
|  +-------------------+   +----------------------------------+  |
|  | register_spa_static|  | API routers (/api/v1/auth, ...)  |  |
|  | (backend/static)  |  | + error handlers (core/errors.py) |  |
|  +-------------------+  +-----------------+------------------+  |
|                       +-------------------+------------------+  |
|                       | services -> SQLAlchemy 2.0 sessions   |  |
|                       | + same-transaction audit (audit/...)  |  |
|                       +-------------------+------------------+  |
+-------------------------------+-------------------------------+
                                v
                +---------------+----------------+
                | PostgreSQL 16 (primary)        |
                | fallback.db (SQLite, startup-  |
                | only latch, never per-request) |
                +--------------------------------+
```

## Frontend

- `frontend/src/main.tsx` mounts the app; `frontend/src/app.tsx` wires
  the router, the auth context and the toast context.
- Pages live in `frontend/src/pages`, shared UI in
  `frontend/src/components` (charts, common, forms, layout, ui), API
  access in `frontend/src/api`, reusable logic in `frontend/src/hooks`.
- The build output (`frontend/dist`) is copied into `backend/static` by
  the `Dockerfile`; nothing else serves the frontend in production.
- Colors and chart palette are documented in
  [design-system.md](design-system.md).

## Backend

- `backend/app/main.py` holds the application factory `create_app()`
  and the SPA serving pattern (`register_spa_static`, with
  `SPA_MOUNT_NAME = "spa"`): when `backend/static/index.html` exists the
  factory mounts `/assets` and a catch-all fallback route so client-side
  routes resolve to `index.html`.
- Routers (`backend/app/routers`) are thin: they validate the request
  body with a Pydantic schema and delegate to services
  (`backend/app/services`), which own transactions and audit writes.
- `backend/app/core/errors.py` registers handlers so every failure
  renders the three-key envelope `{"detail", "code", "field"}` with the
  Appendix B code constants (for example `INVALID_AMOUNT`).
- `backend/app/config.py` loads settings from environment variables,
  then `.env`, then defaults (priority pinned by REQ-ARCH-061).

## Database

- SQLAlchemy 2.0 engine and session factory in
  `backend/app/database.py`, with the PostgreSQL connect-timeout chain
  (`DB_CONNECT_TIMEOUT = 5`) and the SQLite fallback
  (`FALLBACK_DATABASE_URL = "sqlite:///./fallback.db"`).
- The fallback is a startup-only latch (`is_fallback()`): if the primary
  probe fails, the engine is rebuilt against `fallback.db` and the flag
  stays set until restart. The fallback path creates tables via
  `create_all` and seeds system categories, never through Alembic.
- Schema changes ship as Alembic migrations
  (`backend/alembic/versions`, single head `005`); see
  [testing-guidelines.md](testing-guidelines.md) for the migration test
  rules.

## Authentication

- JWT bearer tokens: `backend/app/auth/jwt.py` issues HS256 tokens with
  issuer/audience claims from `backend/app/config.py`;
  `backend/app/auth/dependencies.py` resolves the current user for every
  protected route. Passwords are hashed in
  `backend/app/auth/password.py`.
- The client sends `Authorization: Bearer <token>`; the scheme is
  declared in `openapi.yaml` as `HTTPBearer`. Details and examples are
  in [api.md](api.md).

## Directory structure

```text
+-- backend/
|   +-- app/            FastAPI app (routers, services, schemas,
|   |                   models, auth, audit, core)
|   +-- alembic/        Versioned migrations (head 005)
|   +-- tests/          pytest suite (unit/ and integration/)
+-- frontend/
|   +-- src/            React SPA (pages, components, api, hooks)
+-- e2e/                Playwright end-to-end suite
+-- docs/               This documentation tree
+-- docker-compose.yml  Local db + app composition
+-- Makefile            Task vocabulary (make test, make e2e, ...)
+-- openapi.yaml        Exported API contract (16 paths)
```

## Cross-cutting concerns

- **Audit**: `backend/app/audit/logger.py` adds the `AuditLog` row to
  the caller's session and never commits, so the business write and its
  audit row share one transaction (an audit failure rolls both back).
- **Errors**: the `{"detail", "code", "field"}` envelope and the
  Appendix B codes are owned by `backend/app/core/errors.py`; the
  expense service raises `INVALID_AMOUNT` for the five amount-value
  cases that Pydantic cannot express.
- **Money**: amounts travel as `Decimal` in and 2-decimal strings out;
  the frontend sums money in integer cents. See
  [design-system.md](design-system.md) and
  [testing-guidelines.md](testing-guidelines.md).
- **Configuration and secrets**: `backend/app/config.py` plus the local
  placeholders in `docker-compose.yml`; production secrets are injected
  by the platform.

## Architectural decisions

| Decision | Where | Why |
|---|---|---|
| SQLite `fallback.db` with a startup-only latch | `backend/app/database.py` | Keep the app serving when PostgreSQL is down at startup; never switch per request. |
| Same-transaction audit log | `backend/app/audit/logger.py` | A business write without its audit row must never commit. |
| SPA served by FastAPI | `backend/app/main.py` (`register_spa_static`, `SPA_MOUNT_NAME = "spa"`) | One container, one port, no CORS in production. |
| Three-key error envelope with Appendix B codes | `backend/app/core/errors.py` | Clients branch on `code`, not on message text (`INVALID_AMOUNT` is the flagship case). |
| Settings priority env > `.env` > defaults | `backend/app/config.py` | Same image runs locally and on the host platform. |
| Versioned schema via Alembic, fallback bypasses migrations | `backend/alembic/`, `backend/app/database.py` | The fallback is a degraded read/write mode, not a schema fork. |
| Single exported OpenAPI contract | `openapi.yaml` (see `docs/requirements.md` REQ-DOC-084) | The committed contract equals the runtime schema; the API doc documents what ships. |

Task entry points are in `Makefile`; the local two-service composition
is `docker-compose.yml`; the product requirements the decisions above
answer are in `docs/requirements.md`.

## Layered structure, by layer

The overview above describes the shape; the table below names each
layer, its responsibility, and the code that carries it. Backend
layers are REQ-BE-002 (responsibilities) and REQ-BE-003 (dependency
direction: `main` to routers to services to models, never outward);
the frontend counterparts are REQ-FE-002 and REQ-FE-003 (import
direction: pages may import anything below them, components never
import pages, hooks never import components or pages, API modules
never import React, utils stay pure). The whole-stack statements are
REQ-ARCH-010 (frontend layers: entry, pages, components, hooks,
context, API, utils, types) and REQ-ARCH-020 (backend layers: entry,
config, database, routers, services, models, schemas, auth, audit,
core).

| Layer | Responsibility | Where |
|---|---|---|
| Backend entry | app factory, SPA mount, router wiring | `backend/app/main.py` |
| Backend config | settings, env priority | `backend/app/config.py` |
| Backend database | engine, session, fallback latch | `backend/app/database.py` |
| Backend routers | request parsing only, no business rule | `backend/app/routers/` |
| Backend services | business rules, transactions, audit writes | `backend/app/services/` |
| Backend models | ORM definitions | `backend/app/models/` |
| Backend schemas | wire shapes, `Decimal` in / string out | `backend/app/schemas/` |
| Frontend entry | bootstrap and provider tree | `frontend/src/main.tsx` |
| Frontend pages | route composition | `frontend/src/pages/` |
| Frontend components | reusable UI, never page-aware | `frontend/src/components/` |
| Frontend hooks | data fetching through TanStack Query | `frontend/src/hooks/` |
| Frontend context | global state (auth, month, toast) | `frontend/src/context/` |
| Frontend API | the only place `fetch` is called | `frontend/src/api/` |
| Frontend utils | pure functions, no React import | `frontend/src/utils/` |

Provider responsibilities at the entry layer (REQ-FE-022) are one
concern each: `QueryClientProvider` owns the server cache,
`BrowserRouter` the routing, `AuthProvider` the user and token,
`MonthProvider` the selected `yearMonth`, `ToastProvider` the toast
queue. The selected month lives in MonthContext (REQ-ARCH-079), which
is what lets the month picker drive every chart from one place without
any chart owning month state. The hook inventory (REQ-FE-035) is
auth, categories, expenses (list/get/create/update/delete), budgets
(get/set/delete), the six dashboard queries, and toast; all API calls
go through `frontend/src/api/` and nowhere else (REQ-FE-142).

## Request flows

Login (REQ-ARCH-030) is the canonical cross-stack flow: the user
enters credentials, the frontend POSTs `/auth/login`, the backend
verifies the bcrypt hash, signs a JWT, returns token and user, and the
frontend stores the token and redirects to the dashboard. The agent
layer runs the same flow and the same routes: the agent tools call the
same backend API with the same JWT and there are no special endpoints
for them (REQ-ARCH-077), which is why an agent can be audited exactly
like a browser session.

## Cross-cutting rules

- **Security** (REQ-ARCH-063, REQ-SEC-140, REQ-SEC-141): passwords use
  bcrypt at 12 rounds; tokens use HS256 with an environment secret and
  expire after 24 hours with no refresh token; validation covers
  signature, `exp`, `aud` and `iss`; every query filters by `user_id`;
  cross-user access answers 404 rather than 403; the token lives in
  `localStorage`. Audit rows are written in the caller's transaction
  and are never exposed through the API.
- **User isolation** (REQ-BE-151, REQ-API-112 restated here for the
  backend view): isolation is enforced at the query level, not in the
  router, so a new endpoint cannot forget it.
- **Logging** (REQ-BE-122): passwords, tokens, full request bodies,
  raw emails and database connection strings never reach a log line.
- **Testing** (REQ-ARCH-064): backend unit, backend integration,
  frontend unit, frontend component, and E2E tests each live in their
  own location; see `testing-guidelines.md`.

## Data model decisions

The choices below are the ones a reader is most likely to re-litigate,
recorded with the reason they were made.

| Decision | Rule as shipped | Why |
|---|---|---|
| Primary keys | UUID for every table, generated in Python, never by the database (REQ-DB-002, REQ-DB-130) | Portable across PostgreSQL and SQLite; ids exist before the row is flushed |
| Money type | `NUMERIC(12,2)` (REQ-DB-131) | Exact decimal arithmetic; floats are never authoritative |
| Date types | expense `date` is `DATE`, `created_at`/`updated_at` are `TIMESTAMPTZ` in UTC, `year_month` is `CHAR(7)` (REQ-DB-100, REQ-DB-132) | A `DATE` carries no timezone, so month attribution cannot shift across midnight boundaries |
| Budget key | unique `(user_id, year_month)` (REQ-DB-133) | Exactly one budget per user per month, enforced by the schema rather than by service discipline |
| Audit entity | `entity_id` is a UUID with no foreign key (REQ-DB-134) | One column serves several entity types and survives the deletion of the row it describes |
| Foreign keys | all five relationships declared with explicit `ON DELETE` behavior: `CASCADE` for `user_id`, `RESTRICT` for `category_id`, no cascade for `audit_logs.user_id` (REQ-DB-062) | Deleting a user must not strand expenses silently, and deleting a category must not silently rewrite history |
| Audit rules | same transaction, rollback on failure, no API access, preserved on user delete, JSON-serializable values, IP address extracted from the request (REQ-BE-101) | An audit trail that can be lost or rewritten is not a trail |

## Repository and directory structure

The repository root carries README, product-spec.md, AGENTS.md,
CLAUDE.md, openapi.yaml, docker-compose.yml, render.yaml, Makefile,
`.env.example`, `.gitignore` and LICENSE (REQ-ARCH-050); the tree above
shows the directories. `frontend/` holds `src/` with api, components,
pages, hooks, context, types, utils and test, plus `public/`, the
config files and its own Dockerfile (REQ-ARCH-051). `docs/` carries
architecture, api, process, ai-workflow, design-system,
testing-guidelines, agent-extension-pack, permissions, task-template
and `team/`, with `security/` and `ops/` as sibling evidence trees
(REQ-ARCH-054).

Layout choices (REQ-STRUCT-070, REQ-STRUCT-071, REQ-STRUCT-073): a
single monorepo with top-level `frontend`, `backend`, `e2e`, `docs`,
`security`, `ops` and the agent directories, so one checkout builds and
tests everything; the agent capabilities, hooks, MCP server and
custom-agent each own a top-level directory and are surfaced through
symlinks under `.agents/`, with every symlink carrying a defined
target and purpose (REQ-STRUCT-029); and there is no root `src/` and no
Turborepo or Nx - a flat layout, because the workspace count does not
justify a task runner (REQ-STRUCT-073). Frontend tests sit beside their
source as `*.test.ts(x)` while backend tests stay separated under
`backend/tests/unit` and `backend/tests/integration`
(REQ-STRUCT-072, restated in `testing-guidelines.md`).

The project totals approximately 230 files across root, CI/CD,
frontend, backend, E2E, docs, security, ops and the agent trees
(REQ-STRUCT-040); the count is an order-of-magnitude budget, not a
pin - the documentation gates enumerate the required artifacts by name
rather than trusting a total.

## Maintainability surface

REQ-PROD-026 is the maintainability claim the structure above exists to
serve: the backend is split into routers, services, models and schemas,
the frontend into api, components, pages and hooks, and each split is
the boundary a reviewer can read independently. REQ-PROD-025 (the
accessibility claim) is documented in
`design-system.md` and is the surface the component
tests assert against.
