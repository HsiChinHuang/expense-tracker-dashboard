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

Survey (2026-10-10) refined this placeholder into seven issues (t29..t35)
mapped onto the 17 tasks of Chapter 17 §17.7.2 (6.1..6.17) against merged
phase_5 reality (main @ 1dccd15: backend 244 pytest collected / ruff clean /
mypy 84 source files clean / single alembic head 005; frontend 187 vitest /
`tsc --noEmit` rc=0 / lint exactly 4 `react-refresh/only-export-components`
warnings; merge_test_index 146 entries with SHA-pinned amended anchors
tests[16]=t2 / tests[54]=t9; README 202 lines; `.github/workflows/` holds
exactly ci.yml + e2e.yml + deploy.yml + .gitkeep; `agent-capabilities/`,
`agent-hooks/`, `mcp-server/`, `custom-agent/`, `.agents/`, `CLAUDE.md` and
`docs/permissions.md` all measured ABSENT at repo root; platform issues #3..#31
consumed, so #32+ are free).

**Survey rulings (pinned; groom may refine wording, not these decisions):**

1. **VERIFICATION MODALITY = PER-CLASS RULING (executed / structural /
   deferred), measured not assumed.** Re-measured host facts at survey: no
   network egress (coding_standards forbids `curl`/`wget` AND `uv` resolves
   nothing offline — measured: a probe project declaring `httpx>=0.27` fails
   with "Connection Failed"), no GH runner (Actions untriggerable from this
   harness), docker daemon DOWN (`docker` not present in the WSL distro; the
   win32 CLI's `dockerDesktopLinuxEngine` npipe is absent), WSL node v18.19.1
   and win32 node v24.16.0 both available (js-yaml requireable under BOTH —
   measured), backend uv venv green (244 collected, ruff clean, mypy 84 files,
   head `005`), `httpx` 0.28.1 / `python-jose` 3.5.0 / `pydantic` 2.13.5 /
   `uvicorn` 0.54.0 / PyYAML 6.0.3 already installed, **`mcp` NOT installed
   and NOT installable** (probe: `ModuleNotFoundError`). RULING by class:
   (a) **EXECUTED** — hooks and MCP tools: `agent-hooks/*.py` semantics and
   the four MCP tools' auth-before-dispatch/request-shape behavior run as real
   pytest nodes inside the merged backend suite (`backend/tests/integration/
   test_agent_hooks.py`, `test_mcp_tools.py`) with httpx `MockTransport`
   standing in for the backend — so criteria row 8 ("Hook tests pass") and
   REQ-PLAN-061's "hooks importable / hook tests pass / MCP tools work" rows
   are satisfied by execution; (b) **STRUCTURAL** — skills, subagents,
   symlinks, MCP transport core, the two documents: frontmatter/section/manifest
   parses via the already-installed js-yaml + `python -m py_compile` + TOML
   `tomllib` + line-anchored greps, because their requirement text is
   `Read <file>` / `List <dir>`; (c) **DEFERRED** — live agent-session
   discovery/invocation, the live MCP subprocess against a running backend
   (REQ-PLAN-060 task 6.17 "manual MCP test") and live subagent launch: t35
   records each as `DEFERRED <measured reason>` with the operator live-check
   command. A deferred row is never written as PASS (the phase_5 ruling-5
   discipline, carried forward). Every gate stays hermetic, deterministic and
   fail-before-capable: RED at the pre-merge base (all five new paths measured
   absent) and GREEN after the merge.
2. **NO NEW WORKFLOW FILE — the exactly-3 workflow guard is honored, not
   refreshed.** Measured: index entry tests[131] (t26) asserts
   `ls -A .github/workflows | grep -vE "^(ci|e2e|deploy)\.yml$|^\.gitkeep$"` is
   empty, i.e. adding any sibling breaks a GREEN merged entry. No phase_6
   requirement asks for a workflow (REQ-PLAN-060's 17 tasks name none), so
   phase_6 adds ZERO workflows and every card's composite re-attests the
   exactly-3 set. `mcp-server/pyproject.toml` is therefore a DECLARATION for a
   future network-equipped runner, never a CI step in this milestone (t31
   Constraints). If phase_7/8 ever needs a workflow, that survey must ship a
   card that refreshes tests[131]-class ACs first — recorded here so the next
   survey does not rediscover it.
3. **DEPENDENCY POLICY = ZERO new dependency INSTALLED; exactly one new
   manifest DECLARED, and the `mcp` SDK is BANNED.** Measured: `uv` cannot
   resolve even `httpx` offline, so no card may contain an install step (it
   would be a permanently red gate). `mcp-server/pyproject.toml` declares
   `httpx>=0.27` + `python-jose[cryptography]>=3.3` (REQ-TECH-026 names that
   file as a verification target) and is never synced on this host. Because the
   `mcp` package is uninstallable here, t31 hand-rolls the minimal MCP wire
   protocol (newline-delimited JSON-RPC 2.0: `initialize`/`tools/list`/
   `tools/call`) over stdio — the recorded trade-off of the offline host, which
   also makes the server importable and therefore EXECUTABLY testable in t32.
   The five existing manifests (`package.json`, `frontend/package.json`,
   `backend/pyproject.toml`, `backend/uv.lock`, `e2e/package.json`) are
   byte-frozen for every phase_6 card, so the amended anchors' dependency legs
   (tests[16] styled-family/date-fns forbidden; tests[54] recharts == 2.15.4 +
   react-hook-form/zod pinned) cannot collide: neither entry reads `mcp-server/`,
   `agent-*/`, `custom-agent/` or `.agents/` (verified by scanning all 146
   entries at survey), no entry gains a dependency leg, and the index grows
   only by append.
4. **DISCOVERY SYMLINKS ARE GIT-TRACKED FILE LINKS (mode 120000), FILE-LEVEL
   ONLY.** Measured on this host: `ln -s` works under WSL git, `git add` stores
   mode `120000`, and a `git clone --no-local` performed through **cmd.exe**
   (the same git the pipeline uses) materializes real links whose `cat` returns
   the canonical bytes. RULING: `.agents/skills/<name>.md ->
   ../../agent-capabilities/<name>/SKILL.md` and `.agents/agents/<name>.md ->
   ../../custom-agent/<name>.md` — file-level, link depth exactly 2, never
   directory-level links (a directory link would make the REQ-EXT-004
   `ls -la .agents/skills/` verification list the link instead of the skills).
   Every discovery AC is TWO-part: `git ls-files -s` mode-120000 count + the
   EXECUTED `cat`-through-symlink byte-equality (`cmp`), so "discoverable" is
   proven, not asserted.
5. **NEW TOP-LEVEL DIRECTORIES ARE SAFE FOR EVERY EXISTING INDEX ENTRY —
   verified by scan, not by hope.** All 146 index entries were scanned at
   survey: tests[0] (t0) enumerates ONLY `frontend backend e2e security ops
   .github/workflows` + three tracked `.gitkeep` files (no exhaustive root-dir
   list), so adding `agent-capabilities/`, `agent-hooks/`, `mcp-server/`,
   `custom-agent/`, `.agents/` cannot break it; no entry enumerates the repo
   root exhaustively; the only exactly-count guards are tests[131] (workflows,
   handled by ruling 2) and the t27 e2e-file guards (scoped to `e2e/`).
   `git check-ignore` returns rc=1 (not ignored) for every planned path, so no
   `.gitignore` edit is needed — and `.gitignore` stays byte-untouched.
   Floor policy: mypy stays `>= 83` for the whole milestone (84 observed
   pre-milestone; the two new backend test files raise the OBSERVED count,
   which groom records — t24..t28 all pinned `>= 83` and none refreshed it, so
   this survey does not either). The backend collection floor moves by explicit
   in-text refresh: 244 → **258** at t30 (+14 hook nodes) → **270** at t32
   (+12 MCP nodes); t29/t33/t34/t35 add no test node, and the LAST composite AC
   of every card is excluded from the index append (standing rule).
6. **SCOPE BOUNDARIES against later milestones (no card drift).** The
   AI-workflow documentation set — `docs/ai-workflow.md` (REQ-AI-001..052,
   110..143), `docs/process.md` prose, `docs/team/*`, `CLAUDE.md`
   (REQ-AI-021/REQ-DOC-013) and the criteria-table restatement — stays with
   phase_8_docs; `security/ai-tool-data-policy.md` (REQ-AI-130..134) stays with
   phase_7_security_ops (it is a `security/` artifact and REQ-DOC-030 counts
   that tree at 8 files). phase_6 therefore ships EXACTLY the Criterion-12
   evidence set: the four agent directories + `.agents/` +
   `docs/agent-extension-pack.md` + `docs/permissions.md`. REQ-AI rows whose
   verification target is one of those deferred files are listed uncovered in
   the survey handoff with the owning milestone, never silently dropped.
7. **NO BROAD NO-DRIFT GUARDS (hard-won lesson, WAL seq 467/468 / t28 entry
   #139 class defect).** No phase_6 AC may pin `git diff --quiet <sha> --
   backend`, `-- .github`, or any other broad-path freeze: later milestones
   legitimately touch those paths. Freeze assertions are scoped to the
   NARROWEST real product path (the five named manifest files, individual
   router files) or omitted entirely. Every card ends with its no-drift
   composite as the LAST AC (index-append-excluded), which is where the
   suite/lint/mypy/alembic/index floors are re-attested — the mechanism the
   t24..t28 cards proved green.

**The seven cards (single-responsibility, per the t20..t28 precedent):**

| card | vertical | modality | depends | new nodes |
|---|---|---|---|---|
| t29 | skills: 3 `SKILL.md` + `.agents/skills/` symlinks | structural + executed `cat`-through | t28 | 0 |
| t30 | hooks: `validate-amount.py`, `validate-ownership.py`, `agent-hooks/README.md` + backend hook tests | EXECUTED (14 nodes) | t28 | +14 |
| t31 | MCP core: `config.py`, `auth.py`, `server.py`, copy-only manifest | structural (syntax/ruff/mypy/TOML/greps) | t29 | 0 |
| t32 | MCP tools: 4 modules + hook wiring + README + hermetic `MockTransport` tests | EXECUTED (12 nodes) | t30, t31 | +12 |
| t33 | subagents: `custom-agent/finance-analyst.md`, `qa-reviewer.md` + `.agents/agents/` symlinks | structural + executed `cat`-through | t29 | 0 |
| t34 | docs: `docs/agent-extension-pack.md` + `docs/permissions.md` (separate files, REQ-EXT-083) | structural + count/path cross-gates | t29, t30, t32, t33 | 0 |
| t35 | verification card: script-generated `docs/criteria/agent_pack_verification.md` + 3-row deferral register + composite | executed + attested + deferred | t29, t30, t32, t33, t34 | 0 |

Task mapping (§17.7.2): 6.1–6.3 → t29; 6.4–6.7 → t30; 6.8–6.9 → t31;
6.10–6.13 → t32; 6.12(subagents)/6.13 + `.agents/agents/` → t33; 6.15–6.16 →
t34; 6.14 (symlinks, split with t29/t33) + 6.17 (manual MCP test → t35 deferral
register) + §17.7.4 verification → t35. N = 7; batch_size =
min(5, max(1, ceil(7/3))) = 3 → batches [t29,t30,t31], [t32,t33,t34], [t35];
each file written in its own write call. DAG: 36 nodes / 60 edges.

**RULING 8 — DEPENDENCY-CHAIN MEASUREMENT IS MILESTONE-LOCAL (orchestrator
ruling, 2026-10-10; recorded here because it changes how every future survey
reports the chain).** Measured after this survey's DAG extension
(programmatic longest-path DP over dag.json, 36 nodes / 60 edges, 0 cycles,
0 orphans, Kahn order covering all 36 nodes): the **cumulative** critical path
is **24 edges** — t0,t1,t4,t5,t6,t7,t8,t11,t13,t14,t16,t17,t20,t21,t22,t23,
t24,t26,t27,t28,t29,t31,t32,t34,t35 — while `limits.dep_chain_warn = 10` and
`limits.dep_chain_halt = 20` (docs/config.yaml, which is operator-owned and
MUST NOT be edited by any role). The **milestone-local** maximum chain for
phase_6 is **5 edges** (t28→t29→t31→t32→t34→t35). RULING: `dep_chain_warn` /
`dep_chain_halt` are evaluated on the MILESTONE-LOCAL chain; the cumulative
path is carried as a **WARN-class standing condition**, exactly as
`warn = 10` has been carried since it was surpassed in phase_2. Grounds: the
cumulative reading makes the limit structurally unsatisfiable for ANY
post-phase_5 milestone (the chain grows monotonically; the mandated
milestone-exit verification card alone pushes 19 → 21 even if every card is
attached flat to t28), so under that reading the limit could only ever produce
a guaranteed halt — and `docs/config.yaml` is not editable at role authority
level. phase_5's own review_plan already scored the chain in milestone terms
(19 edges). Consequence for this and every later survey: report BOTH numbers
(milestone-local and cumulative), state which reading the threshold is judged
against, and do not flatten a card graph to chase the cumulative figure —
flattening would break the t15/t23/t28 verification-card precedent and still
breach. `definer:review_plan` MUST evaluate `dep_chain` under the
milestone-local reading with the cumulative path recorded as a standing WARN,
not a blocker.

## phase_7_security_ops — Security and Operations (Phase 7)

Survey (2026-10-12) refined this placeholder into six issues (t36..t41)
mapped onto the 13 tasks of Chapter 17 §17.8.2 (7.1..7.13) against merged
phase_6 reality (main @ f33b048 == origin/main: backend 270 pytest collected
/ 270 green / ruff clean / mypy 84 source files clean / single alembic head
005; frontend 187 vitest / `tsc --noEmit` rc=0 / lint exactly 4
react-refresh warnings; merge_test_index 158 entries with SHA-pinned
amended anchors tests[16]=t2 / tests[54]=t9 (entry SHA-256 cfb84edc... /
cf5babc0...); merge_history 36 entries; README 202 lines; `.github/
workflows/` holds exactly ci.yml + e2e.yml + deploy.yml + .gitkeep; the
`security/` and `ops/` trees hold ONLY their tracked `.gitkeep`; the
Makefile `security:` target is still the t4 stub echo; platform issues
#3..#38 consumed, so #39+ are free).

**Survey rulings (pinned; groom may refine wording, not these decisions):**

1. **SCAN TOOLING IS FETCH-AT-GATE, BANNED FROM THE TREE, AND THE REPORTS
   ARE REAL.** Measured at survey on this host: **network egress WORKS**
   (npmjs ping HTTP 200, api.github.com 403-with-body = reachable,
   pypi.org 200, GitHub release assets 200/302) — the phase_6 "no egress"
   fact was uv-resolution-specific and is superseded for this milestone by
   measurement. `uvx pip-audit` RUNS (2.10.1; probe run against
   `uv export --no-hashes --frozen` of backend/uv.lock found 3 real
   vulnerabilities in 2 packages); `uvx semgrep` RUNS (1.180.0); gitleaks
   downloads and runs (v8.30.1 pinned, linux x64 asset); npm audit runs
   (9.2.0); and trivy v0.75.0 downloads and runs
   (`trivy_0.75.0_Linux-64bit.tar.gz`, HTTP 200 / 51 MB, `trivy --version`
   green, a full `trivy fs --scanners vuln,misconfig --format json` measured
   5m18s cold-cache on this host — the first probe's 404 was a stale
   version guess, corrected by re-measurement). ALL FIVE scan legs are
   therefore EXECUTED on this host; the milestone's DEFERRED rows are the
   live-state ones (ruling 4), never a tool that measurably runs. RULING:
   every scan tool is fetched at gate time into `$HOME/.local/bin` /
   `uvx` (gitleaks pinned v8.30.1) and is **BANNED from the git tree** —
   no binary lands in the repo (the t0 index entry #6 `find security ops
   .github -type f ! -name .gitkeep ...` is empty on MAIN today and the
   merged suite re-runs it on every later card; a committed binary would
   make a GREEN merged entry permanently red, and the phase_7 cards that
   legitimately add the eight `security/` files land AFTER t36 amends
   that entry — see ruling 3). Scan reports are committed artifacts
   (REQ-SEC-070/071, REQ-TECH-074, REQ-PLAN-070 tasks 7.1–7.5).
2. **NO NEW WORKFLOW — the exactly-3 guard stands, and REQ-CICD-073 makes
   a CI security job FORBIDDEN, not merely unnecessary.** Measured again:
   index entry tests[132] (t26) asserts `ls -A .github/workflows` minus
   {ci,e2e,deploy}.yml/.gitkeep is empty. REQ-CICD-073 (Must) states
   security scans are NOT in CI — they run locally and results are
   committed — and REQ-CICD-083 repeats "local only". The orchestrator
   brief floated a "CI security job"; the requirements forbid it, so
   phase_7 adds ZERO workflows and the gate mechanism is instead the
   reproducible `make security` pipeline (t36) plus the committed reports
   (t37/t38). This is the ruling-2 preregistration from phase_6 resolving
   as: no card refreshes tests[131/132]-class ACs because no card needs a
   workflow.
3. **THE STALE t0 GUARD IS AMENDED IN THE FIRST WINDOW — the 6ab7da5 /
   0aee30f / t28 precedent, applied PRE-EMPTIVELY.** Index entry #6 (t0)
   forbids any file under `security/` or `ops/` beyond `.gitkeep`; t37+t38
   add the five scan reports and t39/t40/t41 add the five `ops/` documents
   (t39 3, t40 3 `security/` docs, t41 2 `ops/` docs), so the
   orchestrator's strict-window amendment of entry #6 MUST execute after
   t36 merges and BEFORE the t37 pre-merge gate (the amend script is
   authored by the t36 card as `docs/state/amend_index_entry6_phase7.cjs.ready`,
   the `docs/state/amend_legacy_index.cjs.ready` precedent; the amendment RETARGETS
   the find to exclude exactly the eight REQ-SEC-003 `security/` names and
   the five REQ-OPS-002 `ops/` names, preserving the entry's intent: no
   OTHER file — no binaries, no strays — may ever appear in those trees).
   t36's own composite re-attests the ORIGINAL entry #6 green (t36 adds no
   file to those trees), so fail-before/pass-after stays honest on both
   sides of the window.
4. **VERIFICATION MODALITY = PER-CLASS RULING (executed / structural /
   deferred), re-measured, never assumed.** EXECUTED: the scan pipeline
   itself (t36's `make security` legs run the real tools end-to-end at
   gate time — gitleaks/semgrep/pip-audit/npm-audit are measured runnable
   here) and the SQLite-fallback worked example (t39 re-runs the
   already-green fallback harness nodes — `tests/unit/test_sqlite_fallback.py`
   + `tests/integration/test_sqlite_fallback_api.py` — as the executed
   half of REQ-OPS-042's "follow the steps" while the docker half is a
   live-check row). STRUCTURAL: the eight `security/` and five `ops/`
   documents — every REQ-SEC/REQ-OPS requirement's Verification text is
   "Read <file>" / "List <dir>", so gates are section greps, counts and
   cross-references (js-yaml/python/py_compile where a report must parse).
   DEFERRED (each a named DEFERRAL_REGISTER row with the operator
   live-check command, never written as PASS — the phase_5 ruling-5 /
   phase_6 ruling-1 discipline): (a) LIVE_DEPLOYMENT_STATE — REQ-OPS-
   060/061/062 + REQ-PLAN-071 "deployment record is accurate" + criteria
   §24.2 #17 against the live Render instance (measured at survey: the
   configured URL `expense-tracker-dashboard.onrender.com` answers 404 /
   "Not Found" — no live deployed instance is reachable from this harness,
   so the deployment record is authored from measured repo-side evidence
   and the live-comparison row is DEFERRED, the phase_5 REQ-TECH-060
   precedent); (b) LIVE_AGENT_SESSION / LIVE_MCP_SUBPROCESS /
   LIVE_SUBAGENT_LAUNCH — the three phase_6 deferral rows are RE-TESTED
   here: the harness now has network, but the agent runtime that consumes
   `.agents/` is this pipeline itself (pi-agent drives the run; it does not
   load the project pack) and there is still no live backend session, so
   the rows CARRY FORWARD with re-measured reasons (t41) — plan.md never
   assigned them a phase_7 deliverable, and phase_7 promises no runtime it
   cannot drive.
5. **NO EXACT-COUNT PIN ON THE GROWING INDEX (W10).** The cumulative
   merge_test_index floor is `>= 158` at t36 and grows by each card's
   non-composite appends (t36 +5, t37 +5, t38 +5, t39 +5, t40 +5, t41 +5); every composite
   pins `>= 158` plus the anchors byte-unchanged and green — never an
   exact count. Backend collection stays >= 270 (phase_7 adds ZERO test
   nodes by design; the t32 exact-270 leg lives in stored entry #149 and
   is untouched because phase_7 adds no node), frontend >= 187, lint
   exactly 4, mypy >= 83, README <= 500, workflows exactly 3 + .gitkeep,
   the five named manifests byte-frozen (re-attested by every composite —
   phase_7 touches none).
6. **SCOPE BOUNDARIES (no card drift).** `docs/ai-workflow.md` (REQ-AI-
   001..052, 110..122, 132, 140..142), `docs/process.md`, `docs/team/*`,
   `CLAUDE.md`, the criteria-table restatement and the README 5-minute
   path stay with phase_8_docs; REQ-SEC-072's scan-timing prose verifies
   ONLY against `docs/ai-workflow.md` (its Verification field), a file
   phase_7 must not create — it is recorded as the SCAN_TIMING_DOC
   DEFERRAL_REGISTER row in t41 (not silently dropped, not smuggled in as
   an in-artifact section). The accepted-findings register (REQ-SEC-074)
   lives in `security/agent-security-notes.md` per its own Verification
   field — no extra register file exists, because REQ-SEC-003 pins
   `security/` to exactly eight names (survey ruling). `security/` and
   `ops/` are the ONLY product trees phase_7 may add files to, plus
   `backend/scripts/security_ops_verification.py` +
   `docs/criteria/security_ops_verification.md` (t41, the t23/t28/t35
   generator precedent) and the `Makefile` `security:` target (t36).
7. **NO BROAD NO-DRIFT GUARDS.** No AC pins `git diff --quiet <sha> --
   backend` or any broad-path freeze; freezes are scoped to the five named
   manifests or individual files. Every card ends with its composite as
   the LAST AC (index-append-excluded).

**The six cards (single-responsibility, per the t20..t35 precedent):**

| card | vertical | modality | depends | new nodes |
|---|---|---|---|---|
| t36 | scan pipeline: `make security` real recipe + `security/SCANNING.md` how-to + entry-#6 amend script authored | EXECUTED (real tool fetch + dry-run) | t35 | 0 |
| t37 | dependency/secret scan reports: gitleaks + pip-audit + npm-audit committed artifacts + findings addendum | EXECUTED (tools run at gate) | t36 | 0 |
| t38 | container/code scan reports: semgrep + trivy committed artifacts (both EXECUTED here) + register rows appended | executed (semgrep + trivy, both measured runnable) | t36, t37 | 0 |
| t39 | ops runbook core: `ops/runbook.md` + `ops/health-check.md` + `ops/logging.md` | structural + executed re-proof of existing fallback/health nodes | t36 | 0 |
| t40 | security documents: `security/pr-audit.md` + `security/agent-security-notes.md` + `security/ai-tool-data-policy.md` | structural + executed evidence greps over merged code/tests | t37, t38, t39 | 0 |
| t41 | verification card: generator + `docs/criteria/security_ops_verification.md` + `ops/diagnosis.md` + `ops/deployment-health.md` + deferral register + milestone-exit composite | executed + attested + deferred | t36..t40 | 0 |

Task mapping (§17.8.2): 7.1/7.4/7.5 → t37; 7.2/7.3 → t38; 7.6/7.7/7.8 →
t40; 7.9/7.10/7.12 → t39; 7.11/7.13 + §17.8.4 verification + REQ-PLAN-071
→ t41; the pipeline that makes 7.1–7.5 reproducible (REQ-SEC-071 "read
Makefile", REQ-TECH-074 "run make security") → t36. N = 6; batch_size =
min(5, max(1, ceil(6/3))) = 2 → batches [t36,t37], [t38,t39], [t40,t41];
each file written in its own write call. DAG: 42 nodes / 73 edges (review_plan
W1 correction: the six t41→t37..t41 transitive edges are implied by the t41
frontmatter but intentionally NOT added to dag.json — the 73-edge graph is the
canonical minimal form; phase_6 baseline 60 + 13 new = 73 machine-verified);
milestone-local critical path 4 edges (t36→t37→t38→t40→t41 and
 t36→t39→t40→t41 = 4); cumulative critical path 29 edges (recomputed over
dag.json; review_plan W1 correction from 28) carried as the standing WARN per
ruling 8 — dep_chain is judged MILESTONE-LOCAL (4 < 20 PASS).

## phase_8_docs — Documentation and Polish (Phase 8, REQ-PLAN-080 … 081)

Survey (2026-10-13, MAIN 6a0a899 with phases 1-7 closed) refined this
placeholder into six issues (t48..t53). The scope is the Chapter 15 documentation
tree, the criteria-mapping/evidence layer, and the two accepted residuals that
earlier milestones steered here. Rolling planning: only these six cards are
specified; there is no later milestone, so phase_8_docs is the delivery
milestone and t53 is the project-wide acceptance exit.

**SURVEY MEASUREMENTS that shaped the split (all re-measured at 6a0a899):**

1. **THE ROOT DOCS DO NOT EXIST.** `product-spec.md`, `CLAUDE.md`,
   `openapi.yaml` and `docs/{architecture,api,process,ai-workflow,design-system,
   testing-guidelines,task-template}.md`, `docs/team/` and `screenshots/` are
   all absent (measured with `ls`/`git ls-files`). They were never silently
   dropped: phase_1's survey handoff recorded them as deferred
   ("product-spec.md, CLAUDE.md, process.md, role files, task-template.md …
   review_plan should confirm this mapping"), and every later milestone's
   scope-boundary ruling named them phase_8_docs deliverables. phase_8_docs
   therefore OWNS and must land them.
2. **THE `8d141fb2` PIN IS NOT A STORED PIN.** Measured: `tr -d '\r' < README.md
   | sha256sum` = `8d141fb27377c63d6b6d63abaf1db79f52049225438c78156de91dffe600abce`
   (202 lines) and ZERO of the 188 stored `merge_test_index` entries contain
   that digest. The stored README gates are content greps (entries 27=t4,
   119=t23, 128=t24, 135=t26, 144=t28, 149=t32, 150=t34, 155=t35) plus the
   `<= 500` line-count floor. So the README is EDITABLE in this milestone
   without any historical amendment, provided (a) every existing grep token
   survives and (b) the line floor holds. The `8d141fb2` byte-pin appears only
   inside phase_7 card composites (t39/t40/t42 ac6), which are closed records —
   they are NOT re-run as a freeze on new-main.
3. **NO STORED GATE BLOCKS THE NEW FILES.** No stored entry counts the root
   file set or enumerates `docs/` beyond `docs/criteria` and the two t34
   documents; entry #5 (t0) is a `find`-based allow-list over `security ops
   .github` only. Adding root files and `docs/*.md` / `docs/team/*` /
   `screenshots/*.png` turns nothing red (REQ-DOC-083's "no extra files" is a
   Should and names only peer-review-guide/CHANGELOG/CONTRIBUTING/CODE_OF_CONDUCT,
   none of which this milestone adds).
4. **RENDER.YAML IS POSITIVELY GATED (entry 134, t26).** That stored command
   requires exactly one service + one database, `plan: free`,
   `healthCheckPath: /api/v1/health`, a docker runtime, `DATABASE_URL` via
   `fromDatabase` matching the declared database name, `JWT_SECRET` via
   `generateValue: true`, and the nine Chapter-3 §3.10 keys. Any render.yaml
   edit must satisfy entry 134 (measured today: green). The Chapter 14 §14.4.2
   template carries `region`, `autoDeploy`, `region`-on-database,
   `databaseName`/`user` and a JSON-array `CORS_ORIGINS` value that the current
   file does not — this is the steered "render.yaml phantom keys" residual; the
   divergence is recorded in t49 and resolved there in the direction that keeps
   entry 134 green.
5. **THE RUNBOOK TYPO IS NOT STORED EITHER.** `ops/runbook.md:238` tells the
   reader `make test-e2e`; the Makefile vocabulary is `make e2e` (measured:
   `grep -E "^[a-z-]+:" Makefile` shows `e2e`, no `test-e2e`). No stored entry
   contains the string `test-e2e`, so the one-line prose fix is safe — but
   entries 168-172/185/186 re-count the runbook (7 sections, 28 clauses) and
   entry 182 greps its incident-response pointer, so the edit must not change
   section headings or clause counts. This is the steered "runbook
   `make test-e2e` typo" residual (raised at t39 verify time, invisible to the
   six gates then).
6. **FLOORS CARRIED (W10 discipline, no exact counts on growing sets).**
   backend >= 270 collected / green, ruff clean, mypy Success on >= 87 source
   files, single alembic head `005`, frontend >= 187 passed with 0 failed /
   0 pending / 0 todo, `tsc --noEmit` rc=0, EXACTLY 4 `react-refresh` lint
   warnings, workflows exactly `.gitkeep/ci.yml/deploy.yml/e2e.yml`, the five
   named manifests byte-frozen, README <= 500 lines, `merge_test_index >= 188`
   entries with anchors `tests[16]`=t2 (`cfb84edc…`) and `tests[54]`=t9
   (`cf5babc0…`) byte-unchanged and executed green, byte-pins 131/132/133/135
   executed green, entry 139 (t27) checked by IDENTITY only per the t43 Option
   A-ter precedent.
7. **E2E IS NOT A phase_8 GATE.** t47 (#50, Postgres portability) is in flight
   and #45 is open as t42's closure gate. No phase_8 card may require
   `make e2e`, a live deployment, or a fresh E2E run as a precondition; the
   screenshot card (t51) drives the browser through the already-proven
   local-backend route (t41's `ops/diagnosis.md` worked example on
   127.0.0.1:18137-style host backend + Vite/frontend static serving) and
   records that choice. If E2E is green by the time t51 builds, the operator
   may substitute the compose stack — the card accepts either, evidence-first.
8. **DEFERRALS CARRY FORWARD, NEVER PASS.** The five t41 DEFERRAL_REGISTER rows
   (LIVE_DEPLOYMENT_STATE, SCAN_TIMING_DOC, LIVE_AGENT_SESSION,
   LIVE_MCP_SUBPROCESS, LIVE_SUBAGENT_LAUNCH) are re-tested by t53: SCAN_TIMING_DOC
   CLOSES (its artifact `docs/ai-workflow.md` lands in t50 and the row's
   live_check is a read-check); the other four stay DEFERRED with re-measured
   reasons — a deferred row is never written as PASS (phase_5 ruling 5 /
   phase_6 ruling 1 / phase_7 ruling 4 discipline).

**RULINGS:**

1. **README CHANGES ARE ALLOWED AND REQUIRED** (criteria mapping + 5-minute
   path). Every card that touches README must (a) re-state the CR-stripped
   sha256 it produced, (b) keep the `<= 500` line floor, (c) keep every stored
   grep token of entries 27/119/128/135/144/149/150/155, and (d) carry the
   NEW digest forward as the milestone's byte-pin for later cards — the
   Option A-ter "amend the pin, disclose the amendment" precedent rather than
   an impossible byte-freeze. t49 produces pin-1, t52 produces pin-2 (the
   final), t53 pins the final digest and re-attests it.
2. **`openapi.yaml` IS EXPORTED, NOT AUTHORED.** t49 exports the FastAPI schema
   (`app.openapi()`) to the root file and gates it against the merged contract
   tests; hand-writing a second contract would create a drift source the
   requirements do not ask for (REQ-DOC-014 says the file IS the full 3.1 spec;
   FastAPI emits 3.1).
3. **ONE VERIFICATION GENERATOR, THE t23/t28/t35/t41 CONVENTION.** t53 owns
   `backend/scripts/docs_verification.py` +
   `docs/criteria/docs_verification.md` — the only new executable this
   milestone ships (it reads and measures, it adds no product behavior and no
   test nodes; the backend collection floor stays >= 270 with ZERO new nodes).
4. **SCREENSHOTS ARE MEASURED ARTIFACTS.** t52 commits the four named PNGs;
   the gates are file presence, `file`-measured magic bytes + dimensions
   (consistent viewport) and byte size < 500 KB (REQ-DOC-041). No image
   "content" is asserted by hash — that would be unfalsifiable prose.
5. **NO BROAD NO-DRIFT GUARDS**; freezes stay scoped to named manifests or
   individual files, and every card ends with its composite as the LAST AC
   (index-append-excluded).

**The six cards (single-responsibility, per the t36..t41 precedent):**

| card | vertical | modality | depends | new nodes |
|---|---|---|---|---|
| t48 | process + ownership docs: `docs/process.md`, `docs/task-template.md`, `docs/team/{pm,software-engineer,qa-engineer}.md`, `docs/ownership.md` | STRUCTURAL (section greps + counts) | t41 | 0 |
| t49 | root reviewer surface: `product-spec.md`, `CLAUDE.md`, `openapi.yaml` (exported), README criteria-mapping table + evidence checklist + 5-minute live/local paths, `render.yaml` residual note, `ops/runbook.md` `make e2e` typo fix | STRUCTURAL + EXECUTED greps | t48 | 0 |
| t50 | AI-workflow and process evidence: `docs/ai-workflow.md` (incl. the REQ-SEC-072 scan-timing section that closes SCAN_TIMING_DOC) | STRUCTURAL + executed evidence greps over merged artifacts | t48, t49 | 0 |
| t51 | technical docs set: `docs/architecture.md`, `docs/api.md`, `docs/design-system.md`, `docs/testing-guidelines.md` | STRUCTURAL + cross-reference greps against merged code | t49 | 0 |
| t52 | screenshot evidence: `screenshots/{dashboard,expense-form,budget-page,health-check}.png` + README/ai-workflow pointers | EXECUTED (browser capture, measured file attributes) | t50, t51 | 0 |
| t53 | documentation verification card: `backend/scripts/docs_verification.py` + `docs/criteria/docs_verification.md`, Chapter 24.3 rows 1-15, deferral register re-test, milestone-exit composite | executed + attested + deferred | t48..t52 | 0 |

Task mapping (§17.9.2): 8.1 → t49 (README delta; the phase-1..7 README content
stays), 8.2 → t51, 8.3 → t51, 8.4 → t51, 8.5 → t51, 8.6 → t50, 8.7 → t52,
8.8/8.9/8.10 → t53 as DEFERRED/attested rows (E2E and live deploy are gated by
#45/#50 and the measured 404, rulings 7/8), 8.11 → t53 (deployment-record
re-attestation), 8.12 → t49 + t53, 8.13 → t53 (reviewer walkthrough rows).
Chapter 15 mapping: 15.1/15.3 process half → t48; 15.2 root + 15.10 quick path
+ 15.11 criteria location → t49; 15.3.4 + REQ-AI-110..142 + REQ-SEC-072 → t50;
15.3.1/2/5/6 → t51; 15.6 + 15.11 screenshot location → t52; 15.1.2 documentation
map, 15.9 guidelines, 24.3 acceptance → t53. N = 6; batch_size =
min(5, max(1, ceil(6/3))) = 2 → batches [t48,t49], [t50,t51], [t52,t53]; each
issue written to its own platform issue in its own call. DAG: 54 nodes / 91
edges after this survey's regeneration of `docs/state/dag.json` + `dag.mmd`.
Baseline repair disclosed: the stored phase_7 graph was 43 nodes / 75 edges but
its `nodes[]` omitted t37/t42/t43/t44 even though edges referenced them (and
t42/t45/t46/t47 defect cards were never DAGged at all), so the graph was not
self-consistent; this survey added every referenced endpoint plus the 6 new
phase_8 nodes and their 13 new edges, keeping existing entries byte-equivalent
(strings stay strings, the two existing {id,status,milestone} objects stay
objects). Zero cycles, zero orphans (Kahn machine-verified over the regenerated
dag.json, prerequisite-first order matching the stored convention); cumulative
longest chain 34 edges ending ...t41→t48→t49→t50→t52→t53, milestone-local
critical path 4 edges (t48→t49→t51→t52→t53 and the equal-length
 t48→t49→t50→t52→t53), carried as the standing WARN per the carried
orchestrator ruling (phase_7 precedent: cumulative WARN, dep_chain judged
MILESTONE-LOCAL (4 < 20 PASS).

## phase_9_req_matrix — Per-REQ-ID Coverage Matrix (Strict Standard, operator directive 2026-10-13)

Survey (2026-10-13, MAIN 54bd4b0 / WAL 0f1fb7c, all 56 cards closed, t45 not_planned
-> closed as diagnosis, WAL through 696) opens a NEW final-milestone class of work:
the operator ruled the chapter-level plan->card mapping INSUFFICIENT and demands a
mechanically verifiable per-requirement-ID coverage matrix over ALL 749 REQ ids.
Rolling planning: three cards t57..t59; t59 is the milestone exit.

**SURVEY MEASUREMENTS that shaped the split (all measured at 0f1fb7c):**

1. **749 UNIQUE IDS, 748 HEADING ENTRIES.** `grep -oE 'REQ-[A-Z]+-[0-9]+'
   docs/requirements.md | sort -u` = 749. The heading-form regex
   `^#+ .*REQ-<FAMILY>-<NNN>:` yields 748; the lone non-heading id is
   `REQ-AUTH-001`, which appears ONLY inside the section 3.1 ID-FORMAT EXAMPLE
   code block (never as a requirement entry). The matrix must classify it with an
   explicit documented status (EXAMPLE_REFERENCE) rather than pretend it is a
   requirement - fabricating evidence for it would poison the strict standard.
2. **DIRECT-COVERAGE AUDIT.** Union of ids referenced in `docs/issues/closed/*.md`
   + `docs/criteria/*.md` + `docs/backlog.md` = 500 unique; intersected with the 749
   = 497 directly referenced. The other **252 ids are covered only indirectly** via
   the Chapter-17-task -> card mapping: TEST 32, API 28, AI 26, FE 25, DB 23, BE 20,
   SEC 18, ARCH 16, PLAN 16, STRUCT 16, PROD 12, OPS 8, TECH 7, PROJ 3, CICD 1,
   AUTH 1. (The 3 corpus ids outside the 749 are references to the example id and
   prose forms; they are not matrix rows.)
3. **EVIDENCE-PRESENCE SCAN OVER THE 252.** Only 6 of the 252 ids are named inside
   test/script source (`grep -r REQ- backend/tests frontend/src e2e backend/scripts
   agent-hooks mcp-server custom-agent extensions scripts`) - BE-092..096, DB-091.
   ID-name absence is NOT gap evidence (cards reference ids in closed-card bodies,
   which the matrix also reads); the matrix's evidence rule is pointer-based, not
   name-based.
4. **PRELIMINARY GAP SAMPLE (20 ids across 10 families, subject-matter greps over
   the verification targets each requirement names).** PREDICTED GENUINE GAPS are
   documentation-record gaps, not code gaps: PLAN-100..103 (risk register -
   `grep -i risk docs/plan.md` = ZERO matches; the 'Read the plan' verification has
   no target), PLAN-110/111/112 (nine-step daily workflow / time allocation /
   session discipline - absent from docs/process.md and docs/ai-workflow.md),
   STRUCT-040 (file-count summary) + STRUCT-050..052 (naming conventions) - no
   artifact outside requirements.md, DB-120 + ARCH-081 (data-volume / project
   assumptions - docs/architecture.md names no assumptions), TEST-070 (the
   enumerated not-tested list - docs/testing-guidelines.md has a 'What not to test'
   section but not the REQ-TEST-070 items). ESTIMATE: ~10-20 of the 252 are genuine
   GAPs, ALL remediable by authoring the pointed-to documentation artifacts; ZERO
   predicted product-code gaps. SAMPLED-COVERED (evidence exists, pointer
   resolution is generator work): TEST-012/020/035/038 (backend/frontend test
   files), API-062/080/110 (dashboard routers, openapi pagination envelope,
   Decimal-as-string), BE-071/100, DB-063/080, FE-011/090/143 (zero dark-mode/i18n
   code = the negative assertion holds), SEC-011/042 (agent-security-notes threat
   actors; SQLAlchemy bound params), ARCH-073 (sqlite fallback), CICD-053/OPS-103
   (runbook rollback), OPS-043..048 (ops/diagnosis.md), AI-012/050/102
   (ai-workflow Tools + task-template.md + ai-tool-data-policy inventory),
   TECH-082/083 (pinned FROM tags, pinned `uses:`), PROD-002..007 (product-spec
   User stories), PROJ-002/003/006 (product-spec), TEST-062 (e2e/fixtures/users.ts
   uniqueUser), TEST-081 (ci.yml coverage legs).
5. **TWO HARD ADJUDICATION CANDIDATES surfaced by the scan (groom-time decisions,
   recorded here so they cannot be silently papered over):** (a) REQ-TECH-008
   (date-fns 3) - the product DELIBERATELY banned date-fns (t20 Q4/Q7 rulings;
   `grep date-fns frontend/src` shows the ban comments; package.json has no
   date-fns). The honest matrix status is GAP-with-ruled-deviation or a new
   DEFERRED_RULLED-class pointer to the deviation record; the vocabulary is CLOSED,
   so the generator cannot invent a fifth status - groom must pick the honest
   mapping and disclose it. (b) REQ-FE-121 (Lighthouse > 85, FCP/TTI budgets) - no
   hermetic measurement exists and browser profiling is outside the no-E2E/no-live
   ruling; FE-120's React.lazy/bundle-analysis half is likewise unimplemented
   (measured: no `lazy(` in frontend/src). These two are the predicted GAP ids most
   likely to remain GAP after evidence work; t58 ac3 escalates rather than fakes.
6. **DEFERRALS AND #61 ARE ROWS, NOT WORK.** The 4 DEFERRED LIVE_* keys
   (LIVE_DEPLOYMENT_STATE, LIVE_AGENT_SESSION, LIVE_MCP_SUBPROCESS,
   LIVE_SUBAGENT_LAUNCH, parsed from the DEFERRAL_REGISTER in
   docs/criteria/docs_verification.md) and platform #61 (RENDER_DEPLOY_HOOK secret,
   open by design, operator infra) map their requirement ids to DEFERRED_RULLED
   with register/#61 pointers. Re-adjudicating them into code scope is OUT OF SCOPE
   (standing no-E2E/no-live, docker ban, deploy-deferred rulings).
7. **FLOORS AND PINS CARRIED (t53 convention).** README.md CR-stripped sha256
   `a64efaa2406a22fcab1e18c1564035caf6ff8d24c85b1d8f92817202e6c0d73c` at 308 lines
   is pin-2 FINAL - phase_9 must NOT touch README (pin-3 is forbidden); AGENTS.md
   8340781c, render.yaml 60110dd0, openapi.yaml 6f2a0a3d; backend >= 270 green,
   mypy Success >= 89 files, ruff clean, single alembic head 005; frontend >= 187
   passed, tsc rc=0, lint EXACTLY 4 react-refresh warnings; workflows exactly
   `.gitkeep/ci.yml/deploy.yml/e2e.yml`; merge_test_index >= 217 with the stored
   byte-pinned anchors green by identity. KNOWN ACCEPTED RESIDUALS must not fail
   the matrix: ac_hash dialect cosmetic, README stale-wording rows under pin-2,
   docs/issues/closed/index.md legacy tests-column zeros, t49/t50 truncated digests.

**RULINGS:**

1. **SIXTH GENERATOR, SAME HERMETIC CONTRACT.** t57 owns
   `backend/scripts/req_coverage_verification.py` +
   `docs/criteria/req_coverage_verification.md` - generated, byte-exact-as-generated
   (docs_verification.md convention), no network, no docker (ABSOLUTE DOCKER BAN),
   no live/E2E, no wall-clock and no git metadata in output; two runs byte-identical
   is an executed AC. This milestone adds ZERO pytest/vitest nodes by design.
2. **CLOSED VOCABULARY + FAIL-CLOSED FENCE.** Statuses are exactly
   {IMPLEMENTED_TESTED, IMPLEMENTED_STRUCTURAL, DEFERRED_RULLED, GAP} + the one
   documented structural class EXAMPLE_REFERENCE (REQ-AUTH-001 only). The generator
   EXITS NONZERO iff any row is GAP or any non-GAP row lacks >= 1 concrete evidence
   pointer (test node id, file artifact, criteria report row, or register/#61
   pointer). The matrix closes the loop; it does not merely report.
3. **REMEDIATION IS MEASURED, NOT PRE-COMMITTED.** t58's AC list is generated from
   t57's GAP rows at groom. The survey's predictions (measurement 4) scope the
   estimate only. If t57 measures ZERO GAP, t58 is a no-op card closed by
   attestation and the milestone is matrix + exit composite.
4. **NO SILENT RELABELLING.** An id still uncovered after t58's evidence work is
   escalated as a NEW deferral candidate for operator ruling (t58 ac3); the closed
   vocabulary forbids inventing statuses mid-milestone.
5. **GENERATOR-OWNED CRITERIA DIR.** The five carried reports are never
   hand-edited; matrix flips happen by changing the generator's evidence map and
   authoring the artifacts it points at.

**The three cards:**

| card | vertical | modality | depends | new nodes | platform |
|---|---|---|---|---|---|
| t57 | matrix generator + report (749 rows, closed vocabulary, evidence pointers, fail-closed fence, byte-determinism) | EXECUTED generator + hermetic determinism | t53 | 0 | #62 |
| t58 | gap remediation - author the missing evidence artifacts until the fence reaches 0 GAP (predicted: PLAN risk/workflow records, STRUCT file-count + naming, DB-120/ARCH-081 assumptions, TEST-070 list, PROD success rows; AC set measured from t57 output) | STRUCTURAL docs authoring + matrix re-run | t57 | 0 | #63 |
| t59 | milestone-exit composite - six generators green, matrix closed (0 GAP, 749 rows), floors + byte-pins + workflow freeze + deferral re-attestation, accepted residuals re-listed | executed + attested + deferred | t57, t58 | 0 | #64 |

Local-id numbering verified, not assumed: highest local id across docs/backlog.md +
docs/issues/closed/ is t56 (t54/t55 exist and are closed); this milestone continues
at t57/t58/t59. Platform numbering: highest existing issue is #61 (open by design);
the three cards are #62/#63/#64, each created in its own call, `defined` applied and
read back per issue. N = 3; batch_size = min(5, max(1, ceil(3/3))) = 1 -> batches
[t57], [t58], [t59]. DAG: regenerated docs/state/dag.json + dag.mmd at 60 nodes /
98 edges (the stored phase_8 graph - 54 nodes / 91 edges - never DAGged the
t54/t55/t56 E2E defect cards; this survey added those three closed endpoints and
their backlog-documented edges t54->t47, t55->t54, t56->t55 plus the 3 new nodes and
3 new edges, keeping every existing entry byte-equivalent); zero cycles, zero
orphans, Kahn machine-verified. Cumulative longest chain 37 edges
(...t41->t48->t49->t50->t52->t53->t57->t58->t59); milestone-local
critical path 2 edges (t57->t58->t59), dep_chain MILESTONE-LOCAL per the
phase_6/7/8 precedent, cumulative carried as standing WARN.
