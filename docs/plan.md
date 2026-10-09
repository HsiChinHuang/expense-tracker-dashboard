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

Survey (2026-10-09) refined this placeholder into five issues (t19..t23)
mapped onto the 19 tasks of Chapter 17 §17.5.2 (4.1..4.19) as vertical slices
against merged phase_3 reality (main @ 91124de: five routers on
/api/v1, dashboard_service is the SEVENTH router — append-only in create_app,
no Alembic revision in this milestone, MSW harness with frozen handlers.ts,
inline role=status / role=alert+Retry / <p> empty conventions per t18 Q8,
queryKeys factory whose dashboard family is explicitly a phase_4 extension,
expense/budget mutations already invalidate the ["dashboard"] prefix so
REQ-FE-051 observability closes here).

**Survey rulings (pinned; groom may refine wording, not these decisions):**

1. **recharts ADMITTED, exact pin `recharts` 2.15.4** (REQ-TECH-004 Must,
   "Recharts 2"; registry-verified latest 2.x). The package.json diff is
   owned SOLELY by t21 (the chart-components issue). t19/t20/t23 carry
   ac-gates that FAIL if recharts is present before t21 lands it or after
   t21 if absent — the admission is one-door, test-enforced.
2. **date-fns REJECTED** (REQ-TECH-008 is Should; every phase_4 need —
   "MMM YY" labels, Monday-week grids, day-count month walks, cross-year
   windows — is proven stdlib: merged monthWindow/shiftMonth and the
   backend month_range/add_month/subtract_months helpers (REQ-BE-096) exist,
   and the t18 month helpers passed byte-identical frozen tests). The
   forbidden-dependency grep keeps `date-fns` banned for the whole
   milestone; only `recharts` is admitted. REQ-TECH-008 is recorded as
   deliberately-not-adopted in the survey coverage_check.
3. **LEGACY-INDEX AMENDMENT (definer-owned protocol; orchestrator executes
   BEFORE the first phase_4 merge).** merge_test_index entries **#17 (t2)**
   and **#55 (t9)** contain `/^(recharts|date-fns)$/` forbidden-dependency
   legs that would go permanently red the moment t21 adds recharts. Ruling:
   the stored commands are amended IN PLACE (entry count stays 95; no other
   leg touched; no frozen test titles involved) to the same regex with
   recharts removed from the forbidden set and an exact-version leg added —
   recharts, if present, MUST equal exactly "2.15.4"; date-fns stays
   forbidden. #17 forbidden set becomes `^(styled-components|@emotion/|styled-jsx|@stitches/|@linaria/|react-native-css|date-fns)$` plus
   `if ("recharts" in d && d.recharts !== "2.15.4") exit 1`. #55 becomes the
   same amendment plus a positive leg: `d.recharts === "2.15.4"` required
   (true from t21 merge onward; t21's own pre-merge runs AFTER the
   amendment, so ordering is safe). Only the definer proposes amendments
   (this ruling); builders/verifiers must never edit stored entries — a
   future need routes back through a definer ruling. t21's issue file
   carries the identical protocol text as a carry-forward.
4. **REQ-FE-101/102 component halves land in t20** (`components/ui/empty_state.tsx`,
   `error_state.tsx`) per the t18 Q8 deferral; additive only — merged pages
   keep their inline conventions untouched (frozen titles).
5. **MonthContext is ADDITIVE** (t19): new `context/month_context.tsx`
   providing yearMonth/setYearMonth/prevMonth/nextMonth (REQ-FE-032),
   mounted in main.tsx under QueryClientProvider; merged pages are NOT
   refactored (frozen test files) — budget/expenses pages keep their local
   month state; wiring them is a phase_8 polish candidate with explicit
   byte-identical-title constraints. MonthPicker is a new component in t22.
6. **Six dashboard endpoints** are contract-first pinned in t19 (methods,
   auth, query params, exact response shapes below) — no new tables, no
   migration; aggregation in Python per REQ-BE-092.

> Issue t19:
> - Requirement: REQ-API-060..065, REQ-BE-090..096, REQ-ARCH-032 (backend half), REQ-TEST-017/023, REQ-PROD-014/033 (server-side), REQ-SEC-030/031, REQ-PROD-023
> - Title: Dashboard backend — dashboard_service helpers + six GET endpoints
> - Acceptance:
>     - GET /api/v1/dashboard/{summary,by-category,trend,cumulative,heatmap,recent} per the frozen response contracts; all require auth (401 shape); caller-scoped
>     - dashboard_service with get_summary/get_by_category/get_trend/get_cumulative/get_heatmap/get_recent + month_range/add_month/subtract_months/to_decimal helpers; Python aggregation; zero-month and year-boundary correctness
>     - percentage null iff budget 0; cumulative last point equals month total; heatmap Monday weeks 7-day rows; recent limit default 10 max 50
>     - legacy-index amendment protocol restated as carry-forward; no new deps
> - Files: backend/app/routers/dashboard.py, backend/app/services/dashboard_service.py, backend/app/schemas/dashboard.py, backend/tests/unit/test_dashboard_service.py, backend/tests/integration/test_dashboard_api.py
> - Depends: [t14]

> Issue t20:
> - Requirement: REQ-FE-032, REQ-FE-050 (dashboard keys), REQ-FE-051 (observability), REQ-FE-101/102 (component halves), REQ-ARCH-013, REQ-PROD-036 (rapid month switching)
> - Title: Frontend dashboard data layer — MonthContext, dashboard api/hooks, EmptyState/ErrorState
> - Acceptance:
>     - MonthContext (yearMonth/setYearMonth/prevMonth/nextMonth, default current month) additive in main.tsx; merged pages untouched
>     - api/dashboard.ts six fns + queryKeys.dashboard six keys + use_dashboard_* hooks keyed on context month; ["dashboard"] invalidation now observable via mounted observers
>     - EmptyState/ErrorState components per REQ-FE-101/102 with new tests only; merged inline conventions not rewritten
>     - MSW via server.use overrides (handlers.ts frozen); recharts/date-fns absent gate
> - Files: frontend/src/context/month_context.tsx, frontend/src/api/dashboard.ts, frontend/src/hooks/use_dashboard.ts, frontend/src/components/ui/empty_state.tsx, frontend/src/components/ui/error_state.tsx
> - Depends: [t17, t19]

> Issue t21:
> - Requirement: REQ-TECH-004, REQ-FE-070..073, REQ-PROD-033 (chart-side: top-6+Other, empty months, max===0)
> - Title: Recharts admission + CategoryPieChart, MonthlyTrendChart, CumulativeLineChart, WeeklyHeatmap
> - Acceptance:
>     - package.json diff owned here: recharts pinned exactly 2.15.4; legacy entries #17/#55 amendment executed by orchestrator BEFORE this merge
>     - four chart components in components/charts/ with RTL+MSW vitest tests incl. empty states and over-budget red line
>     - pie merges to top 6 + Other; trend "MMM YY" labels stdlib; heatmap custom 7-col grid handles max===0/missing days
>     - date-fns still banned; tsc/lint/no-any gates
> - Files: frontend/package.json, frontend/src/components/charts/category_pie_chart.tsx, frontend/src/components/charts/monthly_trend_chart.tsx, frontend/src/components/charts/cumulative_line_chart.tsx, frontend/src/components/charts/weekly_heatmap.tsx
> - Depends: [t20]

> Issue t22:
> - Requirement: REQ-FE-062, REQ-FE-074, REQ-FE-100 (KPI skeletons), REQ-ARCH-032, REQ-FE-015, REQ-PROD-014/033 (integration side), REQ-PROD-036 (empty dashboard/loading/rapid switching)
> - Title: DashboardPage — MonthPicker, KPI cards, BudgetProgress, recent list, chart wiring, edge cases
> - Acceptance:
>     - DashboardPage at "/" in ProtectedRoute with header (logo, MonthPicker, user menu), 4 KPI cards, 5 charts, recent list; money strings verbatim
>     - month switch updates all six queries via MonthContext; rapid switching resolves to latest selection only
>     - REQ-PROD-033 UI edge cases: empty month, no budget (percentage null), over-budget red, exactly/top-6 categories
>     - Dashboard link in AppShell nav additive; unique document title
> - Files: frontend/src/pages/dashboard_page.tsx, frontend/src/components/common/month_picker.tsx, frontend/src/components/charts/budget_progress.tsx
> - Depends: [t20, t21]

> Issue t23:
> - Requirement: REQ-PLAN-041, REQ-DOC-010 (dashboard rows), REQ-PROD-020 (Should: warm-cache <2s, aggregation <500ms), REQ-TECH-004 (five charts), REQ-PROJ-004
> - Title: Dashboard verification — criteria 17-26/32, README rows, performance measurement
> - Acceptance:
>     - scripted checks: summary total = sum(by-category) = trend month = cumulative last point; heatmap 7 days/week; recent limit; month-switch invalidation observable
>     - five chart components counted; criteria-mapping rows 17-26 + 32 + README dashboard feature/API rows exist
>     - performance numbers recorded (Should); full suites green with amended #17/#55
> - Files: docs/criteria/dashboard_verification.md
> - Depends: [t19, t22]

## phase_5_infra — Container, CI/CD, Deployment (Phases 5 + 8 deploy items)

Survey (2026-10-09) refined this placeholder into five issues (t24..t28)
mapped onto the 15 tasks of Chapter 17 §17.6.2 (5.1..5.15) against merged
phase_4 reality (main @ 1637162: FastAPI + uv + alembic heads == 005, 230
backend nodes / 187 frontend nodes in 30 files, merge_test_index 120 entries
with amended anchors #17 (t2) / #55 (t9), lint baseline exactly 4 warnings,
`tsc --noEmit` rc=0, `.github/workflows/` holds only the t0 `.gitkeep`,
`e2e/` and `ops/` likewise, health.py reports the honest phase-1 statics
(`DATABASE_BACKEND: Final = "postgresql"`, `fallback_active = False`),
`create_db_engine` carries NO PostgreSQL branch — the docstring names
phase_5_infra as its owner, and `Makefile` ships only {setup, setup-backend,
setup-frontend, frontend-deps, dev, dev-backend, dev-frontend, test,
test-backend, test-frontend, lint, lint-backend, lint-frontend, down,
migrate, seed, e2e, security} — the REQ-TEST-050 `e2e` target is a stub echo
and `test-backend-unit` / `test-backend-integration` / `*-cov` do not exist).

**Survey rulings (pinned; groom may refine wording, not these decisions):**

1. **VERIFICATION MODALITY = STATIC/STRUCTURAL + HERMETIC EXECUTION; the
   docker daemon, GitHub Actions and Render are UNAVAILABLE on this host
   (measured, not assumed).** `docker` CLI 29.8.2 exists under
   `C:\Program Files\Docker\Docker\resources\bin` but `docker version` fails:
   `npipe:////./pipe/dockerDesktopLinuxEngine … cannot find the file
   specified` (Docker Desktop is not running) and WSL has no docker at all.
   GitHub Actions cannot be triggered from this harness and Render cannot be
   reached (network egress is forbidden by coding_standards). RULING: every
   infra AC is verified by (a) file presence, (b) YAML parse + schema
   assertions through the ALREADY-INSTALLED parsers — `js-yaml` ^4.1.0 is a
   root dependency and PyYAML 6.0.3 is resolvable in the merged backend venv
   (`uv run python -c "import yaml"`) — so NO new dependency is needed, and
   (c) hermetic execution of the behavior the artifact encodes (TestClient
   over `create_app` with a private sqlite `get_db` override, per the t23
   recipe). Script-generated evidence documents (t23 precedent) are the
   accepted evidence form for the live-later rows. `docker build` /
   `docker compose up` are NOT verification commands for any AC in this
   milestone; they become the operator's live check (recorded in
   `ops/deployment-health.md`). Every gate stays hermetic, deterministic and
   fail-before-capable: each AC command must be provably RED at base
   `1637162` (the artifacts do not exist yet) and GREEN after the merge.
2. **SQLite fallback (REQ-PROD-017 / REQ-BE-130..133) is a PRODUCT-CODE
   change and is the ONLY product-code delta of the milestone. It is owned
   SOLELY by t25** (`backend/app/database.py` + `backend/app/routers/health.py`
   + one new test file). Contract safety: the merged four-field health schema
   (`DatabaseBackend = Literal["postgresql","sqlite"]`) already admits the
   live values, and the merged `test_health_api.py` assertions are
   `database in {"postgresql","sqlite"}`, `status in {"ok","degraded"}` and
   `(status=="ok") is (fallback_active is False)` — all of which stay
   BYTE-IDENTICAL and GREEN once `database` is derived from the live engine
   dialect and `status` is derived from `fallback_active`. The fail-before
   anchor is the phase-1 constant `DATABASE_BACKEND: Final[DatabaseBackend] =
   "postgresql"` (routers/health.py:15): a gate that asserts its absence is
   RED at base and GREEN after t25. REQ-DB-083 is honored — fallback uses
   `create_all()` + the merged `app.scripts.seed` routine, never Alembic.
   Any NEW backend test lands with frozen byte-exact titles pinned at groom.
3. **Playwright is a DEV TOOLING admission in a NEW isolated workspace
   `e2e/package.json` (t27), pinned exactly `@playwright/test` 1.58.0** — the
   version already present in WSL at `/usr/local/bin/playwright`. RULING on
   executability: the browser store is ABSENT
   (`~/.cache/ms-playwright` does not exist; `playwright install --dry-run`
   shows chromium/firefox/webkit all uninstalled) and downloading browsers
   requires network egress, which the coding standards forbid. Therefore the
   three E2E specs are verified **structurally** in this milestone (config +
   fixture + spec content gates via js-yaml/TS-source assertions) and
   EXECUTION IS EXPLICITLY DEFERRED to the `e2e.yml` CI run on a
   browser-equipped runner — recorded as a deferral in the survey
   `coverage_check` and in `docs/criteria/infra_verification.md`. No new
   dependency touches the root `package.json` or `frontend/package.json`, so
   the amended index anchors #17 (t2) / #55 (t9) dependency legs
   (styled-family + date-fns forbidden, recharts == 2.15.4) are untouched:
   neither leg reads `e2e/package.json`, no index entry gains a dependency
   leg, and the entry count only grows by append. `e2e/` is deliberately
   excluded from the root tsconfig `include` and from `frontend/.eslintrc`
   scope so `tsc --noEmit` rc=0 and the exactly-4-warning lint baseline stay
   green without any Playwright type install.
4. **N = 5 issues.** batch_size = min(5, max(1, ceil(5/3))) = 2 → batches
   [t24,t25], [t26,t27], [t28]; each file written in its own write call.
   Slices: t24 containers (Dockerfile + docker-compose.yml + .dockerignore +
   README local-modes), t25 SQLite fallback + live health (the product
   delta), t26 CI/CD + Render (three workflows + render.yaml + Makefile
   targets), t27 Playwright harness (config, fixtures, three specs,
   e2e/package.json), t28 milestone verification card (t15/t23-style
   script-generated evidence doc).
5. **Live-only requirements are DEFERRED with recorded evidence, never
   faked.** REQ-TECH-060 (open the live URL), REQ-TECH-062 / REQ-CICD-041
   (UptimeRobot monitor exists), REQ-CICD-036 (first deploy) and
   REQ-PLAN-051's "deploy works / E2E passes / UptimeRobot active" rows
   cannot be executed from this harness. t26 ships the artifacts they depend
   on (`render.yaml` with `healthCheckPath`, deploy-hook + health-retry
   `deploy.yml`, README cold-start notice) and t28 records each live row as
   `DEFERRED <reason>` in `docs/criteria/infra_verification.md`. A deferred
   row is never written as PASS.
6. **Scope boundaries against later milestones (no card drift).**
   `ops/` documentation (REQ-OPS-002/020..028/030/040 runbook, health-check,
   diagnosis, logging) and every security-scan artifact stay with
   phase_7_security_ops; the full README/docs tree and criteria-table
   restatement stay with phase_8_docs. t24/t26 therefore add only the README
   sections their own artifacts require (local dev modes; deploy + cold-start
   notice), README staying under 500 lines (116 today).

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
