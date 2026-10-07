# Plan

Tech stack: React 18 + TypeScript 5 + Vite 5 frontend (Tailwind CSS 3, Recharts 2,
TanStack Query 5, React Hook Form 7 + Zod 3, Axios 1, Vitest + RTL + MSW 2);
Python 3.12 + FastAPI 0.110 backend (SQLAlchemy 2 + Alembic, Pydantic 2,
python-jose + passlib[bcrypt], uvicorn, uv, pytest 8, ruff + mypy);
SQLite for local dev / PostgreSQL 16 for Compose and production; Docker +
Docker Compose; GitHub Actions CI; Render free-tier deployment.
(See requirements §7 / REQ-TECH-001 … REQ-TECH-091; REQ entries win over summaries.)

Milestones follow the eight delivery phases of REQ-PLAN-001. Rolling planning:
only the current milestone's issues are generated in full; later milestones are
refined by survey/review_plan when they begin.

> Issue template:
> - Requirement: <requirements.md anchor>
> - Title: <title>
> - Acceptance:
>     - <checkable statement>
> - Files: <file paths>
> - Depends: [<issue ids>]

## phase_1_init — Skeleton and Foundations (Phase 1: Spec and Skeleton, REQ-PLAN-010 … 012)

> Issue template:
> - Requirement: REQ-STRUCT-001, REQ-STRUCT-010 … 012
> - Title: Repository skeleton
> - Acceptance:
>     - backend/ and frontend/ directories exist with the layering of Chapter 16
>     - `git status` shows no tracked secrets or `.env` files
> - Files: backend/, frontend/, e2e/, docs/, .gitignore
> - Depends: []

> Issue template:
> - Requirement: REQ-TECH-020 … 028, REQ-TECH-073
> - Title: Backend skeleton (FastAPI + uv + pytest + ruff/mypy)
> - Acceptance:
>     - `uv sync` installs without error
>     - `uv run pytest` passes with at least one smoke test
>     - `ruff check .` and `uv run mypy .` pass
> - Files: backend/pyproject.toml, backend/app/main.py, backend/tests/
> - Depends: [t0]

> Issue template:
> - Requirement: REQ-TECH-001 … 010
> - Title: Frontend skeleton (Vite + React + TS + Tailwind + Vitest)
> - Acceptance:
>     - `npm install` and `npm test` pass in frontend/
>     - `npx tsc --noEmit` passes
>     - Dev server builds the app shell
> - Files: frontend/package.json, frontend/src/main.tsx, frontend/vite.config.ts
> - Depends: [t0]

> Issue template:
> - Requirement: REQ-PROD-016 (FR-HEALTH-1)
> - Title: Health check endpoint
> - Acceptance:
>     - GET /api/health returns status, database, fallback_active, version
>     - Integration test asserts schema and 200 response
> - Files: backend/app/api/health.py, backend/tests/test_health.py
> - Depends: [t1]

> Issue template:
> - Requirement: REQ-TECH-090, REQ-TECH-091, REQ-STRUCT-020
> - Title: Root configuration (.env.example, Makefile, LICENSE, README)
> - Acceptance:
>     - .env.example contains placeholders only, no secrets
>     - Makefile exposes setup/test/lint targets for both stacks
> - Files: .env.example, Makefile, LICENSE, README.md
> - Depends: [t1, t2]

## phase_2_auth — Authentication (Phase 2, REQ-PLAN-020 … 021)

> Issue template:
> - Requirement: REQ-PROD-010 (FR-AUTH-1…4), REQ-AUTH-*
> - Title: User model and migrations
> - Acceptance:
>     - User table via SQLAlchemy 2 models; Alembic migration applies cleanly
>     - Passwords stored bcrypt-hashed, never in plaintext
> - Files: backend/app/models/user.py, backend/alembic/versions/
> - Depends: [phase_1 issues]

> Issue template:
> - Requirement: REQ-PROD-010, REQ-API (auth endpoints)
> - Title: Register / login / me endpoints with JWT
> - Acceptance:
>     - register, login, me work per error codes; 24-hour JWT lifetime
>     - duplicate email and wrong password rejected with correct codes
> - Files: backend/app/api/auth.py, backend/app/services/auth.py
> - Depends: [phase_2 model issue]

> Issue template:
> - Requirement: REQ-FE (auth pages), REQ-PROD-010
> - Title: Frontend auth (AuthContext, axios client, login/register pages, ProtectedRoute)
> - Acceptance:
>     - login/register flows pass RTL + MSW tests
>     - unauthenticated users are redirected from protected routes
> - Files: frontend/src/context/AuthContext.tsx, frontend/src/pages/Login.tsx
> - Depends: [backend auth issues]

(Refined by survey when this milestone begins.)

## phase_3_crud — Core CRUD (Phase 3, REQ-PLAN-030 … 031)

Scope: categories, expenses, budgets, audit logging, per-user isolation,
frontend pages for expenses/budgets/categories. Decimal money precision,
audit-in-same-transaction, system-category protection (REQ-PROD-011 … 013,
REQ-PROD-015). Refined by survey when this milestone begins.

## phase_4_dashboard — Dashboard (Phase 4, REQ-PLAN-040 … 041)

Scope: six dashboard endpoints, five Recharts chart types, MonthContext,
MonthPicker, KPI cards, edge cases (REQ-PROD-014, REQ-PROD-033).
Refined by survey when this milestone begins.

## phase_5_infra — Container, CI/CD, Deployment (Phases 5 + 8 deploy items)

Scope: Dockerfiles, Docker Compose (db + app), Render deployment, GitHub
Actions ci.yml/e2e.yml, Playwright E2E, SQLite fallback (REQ-PROD-017,
REQ-TECH-040 … 062). Refined by survey when this milestone begins.

## phase_6_agent — Agent Extension Pack (Phase 6)

Scope: agent-capabilities/, agent-hooks/, mcp-server/, custom-agent/ per
REQ-PROD / REQ-AI / REQ-EXT chapters. Refined by survey when this milestone begins.

## phase_7_security_ops — Security and Operations (Phase 7)

Scope: security scanning (gitleaks, semgrep, trivy, pip-audit), security
headers, ops runbooks, monitoring/health pings (REQ-TECH-074, REQ-TECH-076,
Chapter 12/13 requirements). Refined by survey when this milestone begins.

## phase_8_docs — Documentation and Polish (Phase 8)

Scope: docs tree, criteria mapping table, README 5-minute verification path,
screenshot evidence (REQ-DOC chapter, REQ-PROJ-009). Refined by survey when
this milestone begins.
