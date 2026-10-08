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
>     - GET /api/v1/health returns status, database, fallback_active, version
>     - Integration test asserts schema and 200 response
> - Files: backend/app/routers/health.py, backend/tests/test_health_api.py
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

Survey (2026-10-07) refined the three plan templates into five issues (t5..t9),
scoped as DELTAS against merged phase_1 reality: phase_1 shipped NO database
layer, NO Alembic wiring, and NO auth library usage, so the first template was
split into database foundation (t5) + user model/migration (t6); the backend
auth issue was split into crypto/JWT primitives (t7) + endpoints/service
(t8); the frontend template became one issue (t9) since it fits the 6-AC cap.
The Makefile `migrate` stub from t4 is wired up
in t5. Dependency chain is linear per stack: t5 → t6 → t7 → t8 → t9 (t9 also
depends on t2 for the merged frontend skeleton).

> Issue t5:
> - Requirement: REQ-BE-010/011/012, REQ-TECH-021/030/031/032, REQ-ARCH-072, REQ-DOC-051 (migrate target)
> - Title: Database foundation — Settings, SQLAlchemy engine/session, Alembic wiring
> - Acceptance:
>     - Pydantic Settings class with env > .env > defaults precedence, @lru_cache
>     - create_db_engine + get_db (session per request, finally-close), SQLite PRAGMA foreign_keys ON
>     - alembic init/upgrade head/downgrade base run cleanly; Makefile migrate target wired
>     - existing pytest suite still green; ruff/mypy strict clean
> - Files: backend/app/config.py, backend/app/database.py, backend/alembic.ini, backend/alembic/env.py
> - Depends: [t1, t4]

> Issue t6:
> - Requirement: REQ-DB-010, REQ-DB-011, REQ-TECH-032, REQ-SEC-020 (storage column), REQ-PLAN-020 (task 2.1)
> - Title: User model and users-table Alembic migration
> - Acceptance:
>     - SQLAlchemy 2 User model: UUID PK (Python-generated), email/username unique, hashed_password, is_active, timestamps
>     - revision 001 migration applies and re-applies cleanly on SQLite; columns match Chapter 5 §5.3.1
>     - password column stores hashes only (no plaintext column)
> - Files: backend/app/models/user.py, backend/alembic/versions/001_...py
> - Depends: [t5]

> Issue t7:
> - Requirement: REQ-BE-020/021/022/023, REQ-BE-030, REQ-SEC-020/021, REQ-PROD-022
> - Title: Auth primitives — bcrypt password hashing and HS256 JWT module
> - Acceptance:
>     - passlib bcrypt rounds=12 hash/verify helpers
>     - create_access_token with sub/iss/aud/iat/exp/type claims, HS256, 24h lifetime from settings
>     - decode_access_token validates signature/exp/aud/iss/type with fixed algorithms list; alg=none and wrong-alg rejected
>     - production refuses default/empty JWT_SECRET at settings level
> - Files: backend/app/auth/password.py, backend/app/auth/jwt.py
> - Depends: [t5, t6]

> Issue t8:
> - Requirement: REQ-PROD-010 (FR-AUTH-1..4), REQ-API-020/021/022, REQ-BE-041/050/051, REQ-SEC-022/023, REQ-PROD-030 (subset), REQ-ARCH-022/024
> - Title: Register / login / me endpoints with auth service and get_current_user
> - Acceptance:
>     - POST /api/v1/auth/register: 201 + user; 409 DUPLICATE_EMAIL/DUPLICATE_USERNAME; 422 validation
>     - POST /api/v1/auth/login: 200 token+user; 401 INVALID_CREDENTIALS (same code for wrong password and unknown email; dummy bcrypt for timing parity)
>     - GET /api/v1/auth/me: 200 current user; 401 UNAUTHORIZED/TOKEN_INVALID/TOKEN_EXPIRED/USER_INACTIVE
>     - errors use {detail, code, field} shape; router registered in create_app
> - Files: backend/app/routers/auth.py, backend/app/services/auth_service.py, backend/app/schemas/auth.py, backend/app/auth/dependencies.py
> - Depends: [t7]

> Issue t9:
> - Requirement: REQ-FE-010..014/031/040/041/060/061, REQ-TECH-006/007/009, REQ-ARCH-012/013/042/070, REQ-PROD-010
> - Title: Frontend auth — axios client, AuthContext, route guards, login/register pages
> - Acceptance:
>     - axios client: VITE_API_BASE_URL, Bearer interceptor, 401 clears token, error normalization
>     - AuthContext (user/token/isLoading/login/register/logout) validating token via /auth/me on mount; token in localStorage key `token`
>     - ProtectedRoute (spinner + redirect with location state) and PublicOnlyRoute wired in nested route table
>     - LoginPage/RegisterPage with React Hook Form + Zod pass RTL + MSW tests
> - Files: frontend/src/api/client.ts, frontend/src/context/auth_context.tsx, frontend/src/components/route guards, frontend/src/pages/login_page.tsx, frontend/src/pages/register_page.tsx
> - Depends: [t2, t8]

## phase_3_crud — Core CRUD (Phase 3, REQ-PLAN-030 … 031)

Survey (2026-10-08) refined this placeholder into nine issues (t10..t18),
mapped onto the 25 tasks of Chapter 17 §17.4.2 (3.1..3.25) as vertical slices
against merged phase_2 reality (main @ 08bd245: routers/service/schemas pattern,
get_current_user + get_db dependencies, core/errors.py {detail, code, field},
axios client with NETWORK_ERROR normalization, MSW harness, exact-pin policy).
Alembic revisions form a linear chain: 001 users (t6, merged) → 002 categories
(t10) → 003 audit_logs (t12) → 004 expenses (t13) → 005 budgets (t14); each
migration issue therefore depends on the previous migration issue.
Date handling stays stdlib: date-fns (REQ-TECH-008, Should) and recharts
(REQ-TECH-004) remain BANNED in phase_3 per the t9 ac6 forbidden-dependency
grep and the exact-pin policy — YYYY-MM month math is plain string arithmetic;
recharts lands in phase_4 and any date-fns admission is a phase_4 survey
decision. Network-error PRESENTATION (t9 carry-forward #4) lands in t17 with
the ToastProvider. Money is Decimal end-to-end, transmitted as strings
(REQ-PROD-023, REQ-SEC-050); audit writes are same-transaction (REQ-PROD-015,
REQ-ARCH-078).

> Issue t10:
> - Requirement: REQ-DB-020/021/022/023, REQ-DB-070/071/072, REQ-DB-081, REQ-TECH-031/032
> - Title: Category model, Alembic 002, idempotent system-category seed
> - Acceptance:
>     - Category model matches Chapter 5 §5.4 incl. HEX-color and system-consistency CHECKs
>     - revision 002 applies/downgrades cleanly on SQLite; partial unique (user_id,name)
>     - ten system categories seeded idempotently (is_system TRUE, user_id NULL)
> - Files: backend/app/models/category.py, backend/alembic/versions/002_*.py, backend/app/scripts/seed_categories.py
> - Depends: [t5, t6]

> Issue t11:
> - Requirement: REQ-API-030/031/032, REQ-BE-060/061/062/063, REQ-PROD-013/034, REQ-SEC-032/033
> - Title: Categories API — list/create/delete with system protection + access validator
> - Acceptance:
>     - GET returns system + own custom only; POST 201 / 409 duplicate / 422 bad HEX
>     - DELETE 204 own / 404 other-user or unknown / 409 in-use; system rows immutable
>     - validate_category_access service helper reusable by the expense path
> - Files: backend/app/routers/categories.py, backend/app/services/category_service.py, backend/app/schemas/category.py
> - Depends: [t8, t10]

> Issue t12:
> - Requirement: REQ-DB-050/051/052/053/054, REQ-PROD-015 (FR-AUD-1/2), REQ-SEC-060..064, REQ-BE-042, REQ-ARCH-022/078
> - Title: Audit foundation — audit_logs model, Alembic 003, same-transaction logger, get_client_ip
> - Acceptance:
>     - AuditLog model + revision 003 with action/entity CHECKs and JSONB/JSON-portable payload
>     - write helper joins the caller transaction; audit failure rolls back the business write
>     - old_value NULL on CREATE, new_value NULL on DELETE; no audit API endpoint exists
> - Files: backend/app/models/audit_log.py, backend/alembic/versions/003_*.py, backend/app/audit/logger.py
> - Depends: [t6, t10]

> Issue t13:
> - Requirement: REQ-API-040..044, REQ-BE-070..075, REQ-PROD-011/031, REQ-DB-030..034, REQ-DB-090/091, REQ-SEC-050/051, REQ-ARCH-023/031/078
> - Title: Expenses vertical — model + Alembic 004, service, five endpoints, audit integration
> - Acceptance:
>     - expenses table constraints/indexes per §5.5; amount NUMERIC(12,2) Decimal-as-string
>     - POST 201 with validation matrix + 404 foreign category; list filters year_month/category_id, page/page_size default 20
>     - GET/PUT/DELETE 404 on cross-user; audit rows written in the same transaction
> - Files: backend/app/models/expense.py, backend/alembic/versions/004_*.py, backend/app/routers/expenses.py, backend/app/services/expense_service.py, backend/app/schemas/expense.py
> - Depends: [t11, t12]

> Issue t14:
> - Requirement: REQ-API-050/051/052, REQ-BE-080..083, REQ-PROD-012/032, REQ-DB-040/041/042, REQ-SEC-050
> - Title: Budgets vertical — model + Alembic 005, upsert/get/delete endpoints, audit integration
> - Acceptance:
>     - budgets table with UNIQUE(user_id, year_month), amount > 0, YYYY-MM CHECK
>     - PUT upserts (200); GET absent month returns 200 amount "0.00"; DELETE 204 / 404 absent
>     - audit CREATE/UPDATE/DELETE in the same transaction; delete leaves expenses untouched
> - Files: backend/app/models/budget.py, backend/alembic/versions/005_*.py, backend/app/routers/budgets.py, backend/app/services/budget_service.py
> - Depends: [t12, t13]

> Issue t15:
> - Requirement: REQ-SEC-030/031/032/033/034, REQ-PROD-022, REQ-PLAN-030 (3.20), REQ-PLAN-031, REQ-DB-090, REQ-SEC-050
> - Title: Cross-resource user-isolation and money-precision test suite
> - Acceptance:
>     - two-user matrix: B cannot read/update/delete A's expenses/budgets/custom categories (404, no list leakage)
>     - category-access matrix incl. system-category allowance and in-use delete 409
>     - Decimal round-trip exactness incl. aggregation; audit coverage + no audit endpoint
> - Files: backend/tests/integration/test_isolation.py
> - Depends: [t13, t14]

> Issue t16:
> - Requirement: REQ-FE-042/043, REQ-FE-050/051, REQ-FE-034/035, REQ-FE-133, REQ-TECH-005/009, REQ-ARCH-011/070
> - Title: Frontend data layer — typed api modules, queryKeys, CRUD hooks, MSW handlers
> - Acceptance:
>     - api/categories.ts, api/expenses.ts, api/budgets.ts map 1:1 to Chapter 7
>     - queryKeys factory + hooks with REQ-FE-051 invalidation (expenses→expenses+dashboard, etc.)
>     - MSW handlers cover every phase_3 endpoint (literal paths, onUnhandledRequest error)
> - Files: frontend/src/api/categories.ts, frontend/src/api/expenses.ts, frontend/src/api/budgets.ts, frontend/src/api/query_keys.ts, frontend/src/hooks/
> - Depends: [t9, t13, t14]

> Issue t17:
> - Requirement: REQ-FE-063, REQ-FE-080/081/082, REQ-FE-033, REQ-FE-100/101/102/103, REQ-FE-111, REQ-PROD-024/036, REQ-TECH-006
> - Title: ExpensesPage + ExpenseForm modal + ToastProvider (network-error presentation)
> - Acceptance:
>     - ToastProvider in provider nesting; NETWORK_ERROR surfaces a retry affordance (t9 carry-forward #4)
>     - month/category filters, table, pagination, loading/empty states (REQ-FE-063)
>     - create/edit modal with RHF+Zod, blur validation, backend field-error mapping, delete confirm dialog
> - Files: frontend/src/pages/expenses_page.tsx, frontend/src/components/forms/expense_form.tsx, frontend/src/context/toast_context.tsx
> - Depends: [t16]

> Issue t18:
> - Requirement: REQ-FE-064, REQ-FE-065, REQ-FE-080, REQ-FE-100..103, REQ-FE-015, REQ-PROD-012/013 (frontend flows)
> - Title: BudgetPage + CategoriesPage
> - Acceptance:
>     - budget month picker, set/edit form (RHF+Zod), delete confirm, 12-month history composed client-side from the per-month GET contract
>     - categories page splits system (no delete affordance) vs custom (create + delete)
>     - routes wired with unique page titles; RTL + MSW tests for both pages
> - Files: frontend/src/pages/budget_page.tsx, frontend/src/pages/categories_page.tsx
> - Depends: [t16]

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
