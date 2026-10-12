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
