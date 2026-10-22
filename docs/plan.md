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

## phase_8_risk_and_structure_records — Chapter 16/17 records restated from the merged plan (t58 evidence)

The coverage matrix (phase_9 below) measured fourteen planning ids with
no in-repo citation: the Chapter 16 risk register and Chapter 17
phase/milestone structure were carried in this plan's prose but never
named by id anywhere the generator scans. This section restates those
records with their ids attached, in the plan's own terms, measured
against the shipped repository rather than re-idealised. It sits ABOVE
the phase_9 section on purpose: the matrix generator truncates
`docs/plan.md` at its `phase_9_req_matrix` heading, so only this body is
citable and the phase_9 card-mapping rows below stay non-citable.

### Phase and milestone structure (Chapter 17)

The plan runs eight phases. REQ-PLAN-120 is the phase structure
itself: eight phases, sequential, with Phase 4 and Phase 5
parallelizable, estimated 25 days of effort end to end. REQ-PLAN-002
is the dependency rule inside that structure: phases are sequential by
default, and the one sanctioned overlap is Phase 4 and Phase 5 running
in parallel (the dashboard surface and the container/CI surface were
in fact interleaved across t22-t29 and t30-t44). REQ-PLAN-090 is the
milestone layer above the phases: eight milestones M1 through M8,
one per phase, each carrying its own criteria statement; M8 is the
documentation-and-polish milestone whose exit is the Chapter 24
criteria map. REQ-PLAN-011 is the Phase 1 deliverable list: product-spec.md,
AGENTS.md, CLAUDE.md, process.md, the team/ role files, task-template.md,
the repo skeleton, the groomed backlog, the backend and frontend
skeletons, and the root config files - every one of which is present
on `main` today and mapped by the documentation gates in
`docs/criteria/docs_verification.md`.

### Verification records for the early and late phases

REQ-PLAN-021 is the Phase 2 verification record: register, login,
token issued, duplicate email rejected, wrong password rejected,
frontend login renders, frontend redirect after login, and the test
suite green. The shipped evidence is `backend/tests/integration/test_auth_api.py`
(service-level auth), `frontend/src/pages/login_page.test.tsx` and
`frontend/src/context/auth_context.test.tsx` (the frontend login and
redirect legs). REQ-PLAN-050 is the Phase 5 task list, fifteen tasks:
Dockerfile, docker-compose.yml, the health-check endpoint, the SQLite
fallback, render.yaml, the three workflows, the Playwright setup, the
three E2E specs, the first deploy, UptimeRobot monitoring, and the
remaining deploy-hardening tasks; the merged artifacts are the root
`Dockerfile`, `docker-compose.yml`, `render.yaml`, `.github/workflows/`
and `e2e/tests/`, attested by `docs/criteria/infra_verification.md`.
REQ-PLAN-081 is the Phase 8 verification record: README under 500
lines, all docs present, screenshots exist, all tests pass, the live
URL works, and the criteria are mapped. Five of its six clauses are
executed by the documentation gates (README_MEASURE, DOC_MAP_*,
DOC_MAP_SCREENSHOTS, the Chapter 24.3 map); the live-URL clause is the
LIVE_DEPLOYMENT_STATE deferral in the carried register.

### Risk register (Chapter 16) - probability, impact, mitigation

The register below restates the plan's risk rows with the three
required columns (probability, impact, mitigation) for the families
the matrix found uncited. Values are the plan's own estimates, kept
honest against what actually happened.

Technical risks (REQ-PLAN-100, ten rows; the five most consequential
are recorded here with the register's probability/impact/mitigation
shape - the full ten are the Chapter 16.1 table):

| risk | probability | impact | mitigation |
|---|---|---|---|
| Render PostgreSQL free tier expires | high | high | SQLite fallback latch + `ops/deployment-health.md` record |
| Cold start latency | medium | medium | keep the single container small; uptime pinger |
| pi-agent struggles with a task | medium | medium | smaller cards; verifier re-runs every gate |
| Context window limit | medium | high | on-demand doc loading, per-card worktrees |
| MCP tool failure | low | medium | hooks re-validate server-side; fallback to API |

Process risks (REQ-PLAN-101, seven rows: spec too vague, spec so
detailed it stalls, AI writes wrong code, review skipped, issues too
large, correction not written down, session records incomplete). Each
row's mitigation is a pipeline rule that exists in the merged process:
the groomed-card gate, the verifier's independent re-run, the
issue-granularity limits, the correction log in `docs/ai-workflow.md`,
and the session-record requirement.

Scope risks (REQ-PLAN-102, six rows: feature creep, extra charts,
multi-currency, shared budgets, mobile, dark mode). The mitigation for
all six is the same door: anything not in `docs/requirements.md` is
out of scope, recorded in the product spec's scope boundaries, and
rejected at grooming rather than absorbed mid-card.

Deployment risks (REQ-PLAN-103, six rows: deploy failure, migration
failure, cold start, bandwidth limits, build-minute limits, secret
leak). Mitigations as shipped: single-head Alembic with per-migration
tests, the render blueprint kept small, the gitleaks/semgrep scans in
`security/`, and secret injection by the platform rather than
committed `.env`.

Time allocation (REQ-PLAN-111): writing code 40%, reviewing AI output
20%, grooming 10%, testing 15%, docs 10%, debugging 5%. The shipped
pipeline matches the spirit of the split: every card's builder slot is
bounded and a verifier slot re-runs the same gates, so review keeps
its share even when a card moves fast.

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

## phase_10_operator_ux — Operator UX / Local Dev Workflow (operator directive 2026-10-14)

Survey (2026-10-14, base MAIN 2d8bd5c == WAL-727 commit, all 58 cards t0..t59 closed,
highest local id t59, highest platform issue #65, next numbers from #66; first survey
attempt ff1318d0 aborted at worktree allocation on a dirty tree and is NOT a source —
this survey was re-run fresh and read nothing from it) opens a product milestone for
operator-facing defects on the PRIMARY dev host (Windows 11 native, WSL for uv/pytest,
no Docker, SQLite mode). Operator rulings embedded into the cards verbatim:

- **Q1a (README pin-3).** README pin-2 (CR-stripped sha256 a64efaa2..., 308 lines)
  stored in merge_test_index tests[227] is RETIRED as historical evidence at the merge
  of the card that changes README. A NEW pin-3 digest is recorded via a NEW
  merge_test_index entry APPENDED at that merge (orchestrator-owned append). tests[227]
  is NEVER rewritten; no index entry is ever edited or deleted.
- **Q2 (npm scripts).** The dev workflow must be npm scripts in the ROOT package.json
  (pi-agent-orchestrator). frontend/package.json stays byte-identical; zero new
  dependencies; node builtins only.
- **Q3a (logout).** The logout control moves into the AppShell header
  (data-testid `logout-button`); the dashboard's in-page logout button is removed.
  AuthContext.logout behavior is untouched.
- **Q4a (formal flow).** All five concerns go through the formal card flow
  (survey -> review_plan -> groom -> build -> verify -> merge), separate issues.
- **Q6 (auto-fix check).** `npm run check` must AUTO-FIX: a WSL-flavored
  backend/.venv detected on win32 is deleted and rebuilt via `uv sync`; a missing
  node_modules is installed; occupied ports 8000/5173 are reported with PID and
  killed.

**SURVEY MEASUREMENTS that shaped the split (all measured at 2d8bd5c):**

1. **THE ONE-WAY TRAP IS REAL.** frontend/src/app.tsx nests ONLY the index route
   inside `<Route path="/" element={<AppShell />}>`; `/expenses`, `/budgets`,
   `/categories` are SIBLING routes outside the shell, so the nav disappears on those
   pages with no way back except browser Back. app_shell.tsx carries exactly three
   NavLinks (Dashboard/Budget/Categories) — no Expenses link.
2. **THE SAFETY PROPERTY FOR THE MOVE.** All page tests mount page COMPONENTS
   directly (budget/categories/expenses/login/register/dashboard .test.tsx import the
   page, never the router); only dashboard_page_app.test.tsx mounts App at '/' via
   MemoryRouter. Re-nesting the three routes under AppShell therefore breaks no
   existing test.
3. **app_shell.test.tsx IS BYTE-FROZEN** (25 lines, 3 assertions) and stored gate
   tests[110] (t22) enforces `git diff --quiet HEAD -- app_shell.test.tsx`; it has NO
   link-count assertion. All new shell/route proof goes in NEW test files only.
   The frozen test renders <AppShell /> with NO AuthProvider, so the shell-side logout
   control must live in a guard-wrapped subcomponent (useInRouterContext null -> inert,
   same precedent as the shell's NavLink) — the frozen 3 assertions stay green by
   construction.
4. **REQ-FE-010's `*` NotFound ROUTE DOES NOT EXIST** (grep for NotFound across
   frontend/src = zero hits) while the t57 matrix mis-marks REQ-FE-010
   IMPLEMENTED_TESTED via the dashboard_page_app.test.tsx citation and REQ-FE-011
   IMPLEMENTED_STRUCTURAL via the non-existent frontend/src/App.tsx pointer
   (case-lucky match on app.tsx). The matrix is generator-owned; the row re-marks
   itself on the next regeneration once a new test file cites REQ-FE-010 — the
   re-mark belongs to the card that adds the test (its verification regenerates and
   greps the row), not to a hand edit.
5. **GATE-IMPACT SCAN OVER ALL 228 merge_test_index entries** (full-text scan of
   every stored command): tests[27] (t4) greps README for make setup / make
   dev-backend / make dev-frontend / make test / make lint + a quick-start heading —
   all survive a demote-don't-delete README rewrite, so gate[27] is expected GREEN
   after t65. tests[227] (t59 ac4) asserts the pin-2 digest and is the ONLY stored
   gate that can go RED — exactly the gate the operator retired in Q1a. tests[138]
   (t27) greps the literal 'Log out' in e2e/fixtures/helpers.ts (file untouched; the
   button name stays 'Log out'). No stored gate greps logout-button/user-menu/
   'Frontend skeleton' outside the frozen shell test; tests[110]'s app.tsx greps
   (path="/", AppShell element, index DashboardPage) all hold after re-nesting.
6. **docs_verification.py HARD-CODES THE README PIN** (README_DIGEST/README_LINES at
   lines 34-35) and fails README_MEASURE on drift, so the README card must update the
   pin-3 constants and regenerate docs/criteria/docs_verification.md (never
   hand-edited). tests[227] additionally carries docs_verification.md's own
   cr-stripped sha256 29d22aff + blob d849c775 — those legs go RED too, which is the
   same retired-gate consequence, disclosed once.
7. **ROOT package.json HAS NO dev-workflow scripts** (launcher/build/lint/validate
   only); Makefile dev-backend/dev-frontend exist but require make. backend/.venv
   created under WSL is not executable by win32 python — the exact failure Q6
   auto-fix targets.

**CARD SPLIT (5 cards, one concern each per the operator's explicit demand; N=5,
batch_size = min(5, max(1, ceil(5/3))) = 2 -> batches [t62,t63], [t64,t65], [t66]):**

- **t60 #66 — Navigation restructure + NotFound route + Expenses nav link.** MERGED
  (justification): both concerns edit frontend/src/app.tsx; serializing them would put
  two cards on one file for no benefit, and the NotFound route only exists inside the
  restructured tree. Files: app.tsx (re-nest /expenses, /budgets, /categories as
  children of the AppShell route; index DashboardPage unchanged; add `*` NotFound),
  app_shell.tsx (add the 4th NavLink to /expenses), new pages/not_found_page.tsx, new
  test file app_routing.test.tsx. app_shell.test.tsx byte-identical (gate tests[110]).
  New merge_test_index entries appended at merge cover the new proofs; no stored entry
  changes.
- **t61 #67 — Logout into the shell header.** Depends [t60] (serialization: both touch
  app_shell.tsx). New shell-header logout component (data-testid logout-button, name
  'Log out' preserved for the e2e helper), guarded so the router-less frozen shell
  test renders nothing for it; dashboard_page.tsx loses its in-page logout button
  (user-menu span + username stay); auth_context and auth_context.test.tsx
  byte-identical (gate tests[51] pins that test's titles).
- **t62 #68 — npm-script dev workflow in ROOT package.json.** Independent of the
  frontend cards (touches only package.json + new scripts/dev/). Four scripts: check
  (verify + Q6 auto-fix), setup:local (uv sync + alembic upgrade head + npm install
  both stacks), dev (spawn uvicorn + vite, prefixed logs, Ctrl+C kills both, prints
  URLs + health probe), stop (kill listeners on 8000/5173). Windows/macOS-first; node
  builtins only; frontend/package.json byte-identical; Makefile untouched.
- **t63 #69 — README Quick Start rewrite (ALL ENGLISH).** Depends [t60, t62] — it
  documents real merged commands and its pin-3 digest is only derivable after both
  land. npm-script path FIRST (check -> setup:local -> dev -> stop), explicit
  'Stopping the app' section, troubleshooting table (make not found / docker daemon
  down / WSL .venv on win32 / port busy), make content DEMOTED to 'Alternative:
  WSL/Linux with make' (demote, never delete — gate[27] survival measured). Card also
  updates the docs_verification.py pin-3 constants and regenerates the generated
  report. Q1a replay policy: at this card's merge the orchestrator APPENDS the pin-3
  index entry, and tests[227] (with its carried 29d22aff/d849c775 legs) is EXCLUDED
  from the mandatory-green replay set as RETIRED-BY-OPERATOR-RULING-Q1a; the
  replacement is the new entry. tests[27] must replay GREEN.
- **t64 #70 — phase_10 exit composite (milestone exit).** Depends [t60, t61, t62,
  t63]. Adds NO behaviour; attests the conjunction at one commit: full merge_test_index
  replay with tests[227] excluded as RETIRED-BY-Q1a (the exclusion is an
  orchestrator-recorded ruling in the run log, never an index edit), the NEW pin-3
  entry present and green, tests[27] green, every product floor re-measured
  (pytest 288 / ruff / mypy 91 / alembic 005 / vitest >= 187+new / tsc 0 / eslint
  exactly-4), byte-pins (AGENTS 8340781c, render 60110dd0, openapi 6f2a0a3d,
  frontend/package.json byte-identical, app_shell.test.tsx byte-identical, e2e
  workflow files untouched), and the REQ-FE-010/011 matrix rows re-marked with real
  pointers. This card is the recorded home of the pin-2 retirement attestation.
- **t60 additionally carries the matrix note**: after its test lands, the next
  regeneration of the t57 matrix re-marks REQ-FE-010/011 with real pointers; t60's
  verification greps those two rows and fails closed if the mis-mark persists.

DAG: docs/state/dag.json + dag.mmd regenerated to 65 nodes / 105 edges (60/98 + 5 new
nodes t60..t64 + 7 new edges; every existing entry byte-equivalent; t57 status
refreshed 'done' -> 'closed' per the docs/backlog.md ground truth). Kahn
machine-verified: zero cycles, zero orphans. Milestone-local structure: roots =
{t60 nav, t62 scripts}, sink = t64 exit; milestone-local critical path 2 edges
(t60 -> t63 -> t64 and t62 -> t63 -> t64); cumulative longest chain grows by 2 edges
over the phase_9 chain. dep_chain MILESTONE-LOCAL per the phase_6/7/8/9 precedent,
cumulative carried as standing WARN. Platform numbering: highest existing issue is #65
(closed ruling); the five cards are #66..#70, one create call each, labels [defined]
read back per issue. N = 5; batch_size = min(5, max(1, ceil(5/3))) = 2 -> batches
[t60,t61], [t62,t63], [t64]. NO docs/issues/<id>.md card files are created at survey
(the established convention since t44: full five-heading Gate-1 cards are authored at
groom); the platform bodies are DEFINED-stage stubs with the rulings and hard
constraints embedded. README
pin-2 retirement is recorded ABOVE (Q1a) — this appendix section sits AFTER the
`## phase_9_req_matrix` heading on purpose: the matrix generator truncates
docs/plan.md at that heading, so nothing written here can change matrix rows.


## phase_11_readme_demo_seed - README v2 + Demo Seed (operator directive 2026-10-15)

> Operator directive 2026-10-15. This milestone rewrites README.md into a
> reviewer-facing v2 document (ALL ENGLISH, under 500 lines, REQ-DOC-010
> 15-section map preserved, link-style sections acceptable) and adds the
> demo-seed product capability that the README's live-demo section needs.
> This appendix sits AFTER the `## phase_9_req_matrix` heading on purpose:
> the matrix generator truncates docs/plan.md at that heading, so nothing
> written here can change matrix rows.

Tech stack: unchanged (see header). No new runtime dependency; the seed script
is stdlib + SQLAlchemy only.

### Demo-seed anchoring (explicit, binding)

The demo account and its dataset are a NEW operator-directed product
capability with NO REQ-ID anchor in docs/requirements.md. Its authority is
REQ-DOC-010 (the README "live demo" section) plus the operator directive
2026-10-15 (precedent: phase_10 was scoped by the operator directive
2026-10-14). No REQ id is invented for it, anywhere, in any card.

### Pin model (binding for grooms of t66..t70)

- Live pin is pin-3: README cr-stripped digest
  f0fd9eda96a242e4efdb378b2ad4fdc40458d05cd1395ad7088bf21f129995d8,
  367 lines. CORRECTION recorded at t66 groom (definer-verified against the
  index): the digest gate is tests[231] (issue t63, ac pin3); tests[232] is
  t63 ac1, the npm-first Quick Start checker. Earlier WAL/plan text
  misattributed the pin to tests[232]. t66..t70 may turn tests[231] RED as
  the sanctioned pin-leg; t71 performs the sole pin-4 switchover.
- t66..t70 each change README.md content while the stored pin gate stays at
  pin-3. Their gates therefore use a CARD-SCOPED MEASURED-DIGEST
  ATTESTATION (each card reports the cr-stripped sha256 + line count of the
  README it produced; the verifier confirms the working bytes match)
  instead of stored-pin equality. The verifier replays the stored pin-3
  entry and records its RED as the named, sanctioned pin-leg exemption in
  the run log - never as a regression. Every intermediate card body states
  "this card does not touch pins".
- tests[128] is the README CRLF working-bytes/anchor pin (9c56e9ff... at
  pin-3): token/anchor greps, CRLF-tolerant; every README card keeps
  README.md pure ASCII with CRLF working bytes.
- t71 is the SINGLE pin-4 switchover: README digest+line-count re-pin (new
  index entry appended at merge after a verbatim GREEN replay - the Q1a
  append pattern), retirement settlement of tests[227] (Q1a ruling pattern:
  orchestrator-recorded exclusion, NEVER an index edit), update of the
  STALE pin-2 constants in backend/scripts/docs_verification.py (currently
  a64efaa2 / 308L at lines 34-35), and regeneration of
  docs/criteria/docs_verification.md via the generator.
- Carried gates that must survive the rewrite verbatim (measured over all
  237 merge_test_index entries at the phase_11 base): the t63 ac1-ac5
  checker family (npm-first Quick Start, Stopping the app, Troubleshooting
  table, Alternative/make-demoted + Prerequisites-caveat, ASCII), tests[27]
  (t4 quick-start/running-tests/make-tokens/MIT grep set), tests[128],
  tests[135] (Render/deployment headings + REQ-CICD token set + <=500 lines
  + no deploy-hook URL), tests[201] (exactly-15 Chapter 24.3 criteria rows).
  t70's Render PLACEHOLDER therefore keeps the entire tests[135] heading/
  token set; removing it would need a named operator retirement ruling, not
  a card decision.

### Card split (7 cards, N=7; batch_size = min(5, max(1, ceil(7/3))) = 3 -> batches [t65,t66,t67], [t68,t69,t70], [t71])

> Issue template:
> - Requirement: NO REQ anchor (operator directive 2026-10-15; authority REQ-DOC-010)
> - Title: Demo-seed product capability - seed_demo.py + npm run seed:demo
> - Acceptance:
>     - backend/app/scripts/seed_demo.py creates demo@example.com / demo-password-123,
>       system categories, ~90 days of plausible expenses, budgets
>     - root package.json gains "seed:demo"; idempotent wipe+rebuild; non-demo users
>       untouched; deterministic (fixed seed)
> - Files: backend/app/scripts/seed_demo.py, package.json, backend tests
> - Depends: []
> - Platform: #71

> Issue template:
> - Requirement: REQ-DOC-010 (README slimming precondition for v2)
> - Title: Move internal reviewer sections out of README into docs/verification.md,
>   docs/development.md, docs/screenshots.md with one-line README links
> - Acceptance: three docs files exist holding the relocated content; README keeps
>   one-line links; the tests[128] token set stays greppable in README; no pins moved
> - Files: README.md, docs/verification.md, docs/development.md, docs/screenshots.md
> - Depends: [t65]
> - Platform: #72

> Issue template:
> - Requirement: REQ-DOC-010 (title, live demo, features sections)
> - Title: README v2 sections 1-2 - pitch, features, screenshots link, online-demo
>   placeholder with the fixed demo account
> - Acceptance: pitch is internal-vocabulary-free; online-demo section names
>   demo@example.com / demo-password-123 and npm run seed:demo; live URL is a stated
>   placeholder (residual #61); carried gates green except the sanctioned pin-3 exemption
> - Files: README.md
> - Depends: [t66]
> - Platform: #73

> Issue template:
> - Requirement: REQ-DOC-010 (quick start prerequisites)
> - Title: README v2 section 3 - Prerequisites stated plainly: no Python/Docker/make
>   knowledge needed, npm only
> - Acceptance: plain statement that Python/Docker/make/bash knowledge is not needed;
>   host list = Node.js 20+/npm + uv + Git; t63 ac4 prerequisite legs + tests[27] green
> - Files: README.md
> - Depends: [t67]
> - Platform: #74

> Issue template:
> - Requirement: REQ-DOC-010 (quick start, tests entry)
> - Title: README v2 sections 4-6 - run-locally flow: npm run check -> cp .env.example
>   .env -> npm run setup:local -> npm run dev -> open http://localhost:5173 (NOT
>   127.0.0.1); first-run register; demo data via npm run seed:demo; stop via npm run stop
> - Acceptance: eight-step flow in order; localhost host; t63 ac1/ac2/ac3 checkers
>   replay verbatim GREEN
> - Files: README.md
> - Depends: [t68]
> - Platform: #75

> Issue template:
> - Requirement: REQ-DOC-010 (tests, API docs, security/ops sections) + REQ-CICD-036
>   family token custody (carried gate)
> - Title: README v2 sections 7-9 - troubleshooting, API overview, Render deployment
>   PLACEHOLDER only
> - Acceptance: four carried troubleshooting rows survive; API overview links
>   docs/api.md + openapi.yaml; Render section is a placeholder that keeps the full
>   tests[135] heading/token set, fabricates nothing, cites residual #61
> - Files: README.md
> - Depends: [t69]
> - Platform: #76

> Issue template:
> - Requirement: REQ-DOC-081 / REQ-PROJ-005 (criteria mapping) + pin settlement
> - Title: README v2 sections 10-12 + the SINGLE pin-4 switchover
> - Acceptance: exactly-15 criteria rows (tests[201] green); project structure;
>   MIT + AI-workflow pointers; docs_verification.py pin constants moved to the
>   measured pin-4 values + report regenerated; full carried-gate replay with ONLY
>   the two named retired-pin exclusions (tests[227] pin-2, pin-3 entry)
> - Files: README.md, backend/scripts/docs_verification.py,
>   docs/criteria/docs_verification.md
> - Depends: [t70]
> - Platform: #77

### Dependencies and DAG

t65 independent; t66 depends [t65] (the README must only reference the demo
command once it exists); t67..t70 chain t66 -> t67 -> t68 -> t69 -> t70
(same file, serialized, one writer at a time); t71 depends [t70].
Milestone-local dep_chain = 6 edges (t65 -> t66 -> ... -> t71), within the
warn-10 / halt-20 limits. Global DAG: docs/state/dag.json + dag.mmd
regenerated to 72 nodes / 111 edges; Kahn machine-verified zero cycles,
zero orphans.

### Standing constraints for every card in this milestone

- No Docker locally; git writes via cmd.exe.
- README is a reviewer-owned root doc (docs/ownership.md: reviewer-approved
  definer). HUMAN-REVIEW RULING (operator, 2026-10-15, after t66; clarified
  same day: 嚴謹檢查，不可以放水或改驗收標準): the per-card operator
  approval of README diffs is WAIVED for the remaining phase_11 README cards
  (t67-t71). INSTEAD the orchestrator performs a mandatory, RIGOROUS pre-merge
  re-check of the README diff: full heading-level diff, line-by-line scan of
  removed lines against the carried-token/gate set, every carried stored gate
  replayed on the branch tip, ASCII/CRLF/line-budget measured not assumed,
  no fabricated URLs, no internal vocabulary, delta-envelope purity. The
  waiver touches ONLY who signs the Gate-3 review - it does NOT relax, remove
  or weaken any AC, fence, replay, digest attestation, or verifier requirement;
  acceptance criteria are exactly as groomed. The re-check is WALed as the
  Gate-3 review evidence with its measurements. t66 remains fully approved on
  the record (operator packet + explicit approval, WAL 800).
- Single-container architecture (backend serves the built SPA); SQLite
  fallback is a startup-only latch; money as 2-decimal strings; pagination
  {items,total,page,page_size}; JWT HS256 24h.
- README.md stays pure ASCII, ALL ENGLISH, CRLF working bytes.
- docs/state/merge_test_index.json is orchestrator-owned; no card branch
  edits it. Pin moves happen ONLY by orchestrator append at merge.
- NO docs/issues/<id>.md card files at survey (established convention since
  t44): full five-heading Gate-1 cards are authored at groom; platform
  bodies are DEFINED-stage stubs with the rulings and hard constraints
  embedded.
- Platform numbering: highest existing issue was #70 (closed); the seven
  cards are #71..#77, one create call each, labels [defined] read back per
  issue.

---

## phase_12_readme_ux_fixes - Offline-verification README fixes and two form UX defects (operator directive 2026-10-16)

**Origin.** The operator cloned the repository fresh, followed `README.md`
Quick Start verbatim, and it failed at step 1; then tried the demo path and
the two category-touching forms, and hit three more defects (which terminal
runs `npm run seed:demo`, a bare 36-char UUID field, a bare colour field with
no format hint). This milestone is the operator-reported-defect batch: one
README hotfix card and two small frontend cards. Base for the milestone is
`594c817` (main tip at survey time; the README there is 391 lines, pure ASCII,
CRLF, cr-stripped sha256 `5889496439a8d24f4ff6179272a52f6e0333eedfc8c32c336f65833a3ceb4dc0`,
which is the CURRENT live pin-4 value also carried in
`backend/scripts/docs_verification.py` lines 34-35; `docs/state/merge_test_index.json`
holds 259 entries, cr-stripped sha256 `a77f98a0117d1d0b07695f2d1a1a34a3b1bbb2dcccf8687cc0f0d5a21cb578f4`).

**Reproductions this plan relies on (commands actually run at survey).**

| claim | command actually run | measured result |
|---|---|---|
| `npm run check` fails with the tsx message on a fresh clone | `cmd.exe /c "mkdir %TEMP%\t72repro\scripts\dev" && cmd.exe /c "copy /Y <repo>\package.json %TEMP%\t72repro\ && copy /Y <repo>\scripts\dev\*.ts %TEMP%\t72repro\scripts\dev\ && cd /d %TEMP%\t72repro && npm run check"` | prints `> pi-agent-orchestrator@1.0.0 check` / `> tsx scripts/dev/check.ts` then `'tsx' ... is not recognized as an internal or external command.` (codepage-garbled rendering of the same sentence); with the root `node_modules` present the same command prints `[check] platform=win32 native=yes (node v24.16.0)` |
| tsx is a ROOT dependency and every npm script invokes it | `grep -n '"scripts"' -A 20 package.json; grep -n '"tsx"' package.json` | lines 11-24: every script line begins `tsx ...`; line 30 `"tsx": "^4.7.0"` inside `dependencies` |
| the API reads `backend/.env`, not the repo-root file | `grep -n "env_file" backend/app/config.py` -> line 29 `env_file=".env"`; `grep -n "cwd" scripts/dev/dev.ts` -> line 59 `cwd: backendDir()` on the uvicorn spawn | CWD-relative `.env` + uvicorn started with cwd=`backend` => the file the API would read is `backend/.env` |
| no repo-root `.env` is needed offline | `grep -n "env" scripts/dev/check.ts` (only `backend/.venv` lines), `grep -rn "\.env" scripts/dev/*.ts` (only `FORCE_COLOR`), `grep -rn "import.meta.env" frontend/src` (only `frontend/src/api/client.ts:84` `VITE_API_BASE_URL ?? ''`), `sed -n 1,20p frontend/vite.config.ts` (proxy `/api` -> `http://127.0.0.1:8000`) | check / setup:local / dev read no `.env`; vite needs no env file because the proxy is in `vite.config.ts` |
| every app default equals the example value | `sed -n 30,45p backend/app/config.py` vs `grep -n "DATABASE_URL\|JWT_SECRET\|CORS_ORIGINS\|ENVIRONMENT" .env.example` | `sqlite:///./dev.db`, `change-me`, `["http://localhost:5173"]`, `development` on both sides; `grep -n "change-me" backend/app/config.py` -> line 16 placeholder, rejected only in the `ENVIRONMENT == "production"` model validator |
| the expense form demands a raw UUID | `sed -n 108,124p frontend/src/components/forms/expense_form.tsx` | label text `Category id`, plain `<input>` bound to `category_id`; `grep -n "\.id" frontend/src/pages/categories_page.tsx` -> `category.id` is used only as a React `key`, never printed |
| the category colour format and its failure mode | `grep -n "HEX_COLOR_PATTERN" -A 3 backend/app/schemas/category.py` -> line 24 `HEX_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"`, line 47 `color: str = Field(pattern=HEX_COLOR_PATTERN)`; `grep -rn "ck_categories_color_format" backend/app/models/category.py` -> line 55 `sa.CheckConstraint(COLOR_CHECK_SQL, name="ck_categories_color_format")` | schema regex + DB CHECK; the frontend's only client-side leg is `frontend/src/utils/validation.ts:120-127` (`color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, 'Color must be a 6-digit HEX value')`) with no placeholder and no example in the input |

**DISCLOSED FACTPACK DIVERGENCE (do not silently adopt the factpack wording).**
The operator-approved brief describes `backend/.env.example` whose defaults
include `CORS http://localhost:5173,http://localhost:4173` and
`EXTERNAL_API_ENABLED=false`. Measured at the `594c817` base, neither the file
nor those values exist: `git ls-tree 594c817 backend/ --name-only` lists no
`.env.example`, `git ls-files | grep -i example` lists only the repo-root
`.env.example`, and `grep -rn "EXTERNAL_API" backend/app` plus
`grep -rn "4173" backend/app` return zero application hits. The card therefore
cites the repo-root `.env.example` and the `Settings` defaults it can actually
point at, and never prints a `4173` origin or an `EXTERNAL_API_ENABLED` key
into the README. The CWD-relative-`.env` claim (the part the operator needs)
is verified above and stands.

### Milestone issue template (three cards, exact operator-approved split)

> Issue template:
> - Requirement: REQ-DOC-010 (README as the operator entry point) + operator
>   directive 2026-10-16 (offline verification failed on a fresh clone)
> - Title: t72 README offline-verification hotfix - add `npm install`, mark the
>   `.env` step optional with the `backend/.env` location stated, add the tsx
>   troubleshooting row, strengthen the `seed:demo` instructions, and perform
>   the SINGLE pin-5 switchover by cross-consistency
> - Acceptance:
>     - Quick Start carries an explicit `npm install` step before any `npm run`
>       command, the numbered-step gate is restated from EIGHT to NINE steps in
>       the fenced order, and the carried `tests[232]`/`tests[250]`/`tests[251]`/
>       `tests[252]` npm-first + eight-step gates are dispositioned line-by-line
>       (the step-count leg is the ONE sanctioned rewrite; the order legs stay)
>     - the .env step survives with its carried `cp .env.example .env` token
>       and its two carried claim legs, is marked optional for offline local
>       mode, and states that the API reads `backend/.env` (uvicorn runs with
>       cwd=`backend`) while check / setup:local / dev read no .env at all
>     - `## Troubleshooting` gains the tsx row (row-class gates are >=1-per-class
>       and row count is >=5, so a fifth row is additive-safe)
>     - the `seed:demo` step states: second terminal, `npm run dev` keeps
>       running, no restart, nothing visible afterwards, results appear only in
>       the browser as `demo@example.com`, log out first if signed in elsewhere
>     - README invariants hold: <=400 lines (9 lines of headroom, so a line
>       budget is declared and overflow prose may move to `docs/` with a
>       one-line pointer), pure ASCII, uniform CRLF, trailing CRLF, exactly 17
>       level-2 headings, no placeholder language, all-English, and the distinct
>       full-form requirement-id set is unchanged (`01f36118...` per `tests[256]`)
>     - pin-5 switchover by the t71 ac4 CROSS-CONSISTENCY pattern: measured
>       README digest/lines == `docs_verification.py` constants == regenerated
>       report; new values differ from pin-2/pin-3/pin-4 and the base; retired
>       pins `tests[227]`/`tests[231]` stay untouched
> - Files: README.md, docs/development.md (only if prose is relocated),
>   backend/scripts/docs_verification.py, docs/criteria/docs_verification.md
> - Depends: []
> - Platform: #78

> Issue template:
> - Requirement: REQ-FE-081 / REQ-FE-082 (ExpenseForm), REQ-FE-034 (data hooks),
>   REQ-FE-065 (categories surface); operator directive 2026-10-16
> - Title: t73 expense form category dropdown - replace the bare Category-id
>   UUID input with a select populated from the existing categories query
> - Acceptance:
>     - the category control is a `select` populated from `use_categories`
>       showing category NAMES (system rows plus the caller's own custom rows)
>       and submitting a valid `category_id`
>     - editing an existing expense preselects that expense's category
>     - when no suitable category exists the form points at the Categories page
>     - the bare-input pins are dispositioned explicitly, not silently:
>       `expense_form.test.tsx:40` + `:328` (`getByLabelText('Category id')`),
>       `categories_page.test.tsx:83-90` is out of scope, and
>       `e2e/fixtures/helpers.ts:84` (`dialog.getByLabel('Category id').fill(id)`)
>     - backend, API, DB, seed and README are untouched
> - Files: frontend/src/components/forms/expense_form.tsx,
>   frontend/src/components/forms/expense_form.test.tsx,
>   e2e/fixtures/helpers.ts (+ frontend/src/pages/expenses_page.test.tsx only
>   if a measured pin in it breaks)
> - Depends: []
> - Platform: #79

> Issue template:
> - Requirement: REQ-FE-065 / REQ-FE-080 / REQ-FE-082 (CategoryForm),
>   REQ-DB-070 family (colour format), operator directive 2026-10-16
> - Title: t74 category form colour and icon UX - native colour picker plus a
>   `#RRGGBB` text field with example, live swatch, client-side validation and
>   an icon hint
> - Acceptance:
>     - `<input type="color">` plus a text field whose placeholder shows the
>       `#RRGGBB` example, with a live swatch preview
>     - a fixed neutral default colour `#6B7280`
>     - client-side validation uses a regex byte-identical to `HEX_COLOR_PATTERN`
>       quoted FROM `backend/app/schemas/category.py` line 24 by the card (not
>       from memory), with a human-readable error message
>     - the icon label carries a hint of the form `(optional, e.g. utensils)`
>     - the card explains what the colour is for (per-category chart colours -
>       `frontend/src/components/charts/category_pie_chart.tsx` renders
>       `row.color` verbatim as the slice fill)
>     - frontend validation is advisory; the backend schema and the
>       `ck_categories_color_format` DB CHECK stay the final gate
>     - the `getByLabelText('Color')` pins in `categories_page.test.tsx:84` are
>       dispositioned explicitly
>     - backend, API, DB, seed and README are untouched
> - Files: frontend/src/components/forms/category_form.tsx,
>   frontend/src/pages/categories_page.test.tsx
> - Depends: []
> - Platform: #80

### Split rationale (the operator asked explicitly about finer splitting)

- **t72 stays ONE card.** All four README items edit the same file and land on
  the same measured digest. Splitting them would force a pin switchover per
  card (each README change moves the digest) and could not be parallelised,
  because README.md has exactly one writer at a time.
- **t73 and t74 are SEPARATE cards.** Their file and test ownership is
  disjoint (`expense_form.tsx` + `expense_form.test.tsx` + `e2e/fixtures/helpers.ts`
  versus `category_form.tsx` + `categories_page.test.tsx`), so they can run as
  parallel worktrees, and each stays small enough to groom in one run.
- **General rule recorded for future surveys:** same-file / same-pin-domain
  changes merge into ONE card; disjoint file ownership splits.

### Dependencies, DAG and scheduling

All three cards have `depends: []` - t72 touches only README + the docs
verifier, t73/t74 touch disjoint frontend files, and none of them depends on
another's output. Milestone-local dep_chain = 0 edges, far inside the
warn-10 / halt-20 limits. Global DAG: `docs/state/dag.json` + `dag.mmd`
regenerate to 75 nodes / 111 edges (72 + 3 nodes, no new edges); Kahn is
machine-verified with zero cycles and zero orphans.

`docs/state/snapshot.json` currently reports `max_slots: 2`
(`.env MAX_SLOTS=2`, which takes precedence over `docs/config.yaml slots.max=3`),
so at most two cards run concurrently. **Scheduling note for the orchestrator:
t72 goes first; t73 and t74 are the parallel pair.** t72 owns the README pin
domain and the `docs_verification.py` / report regeneration, so it must not be
co-scheduled with anything that could re-pin; the two frontend cards are the
only safe concurrency and they are the only pair that needs it.

### Standing constraints for every card in this milestone

- No Docker locally; git writes via cmd.exe. Platform CLI via cmd.exe from the
  repo root (the Bash tool is WSL and its `node_modules` esbuild is the wrong
  platform).
- README.md is a reviewer-owned root doc (`docs/ownership.md`). The phase_11
  HUMAN-REVIEW RULING (operator, 2026-10-15: per-card approval WAIVED for the
  README cards, replaced by a mandatory rigorous orchestrator pre-merge
  re-check, and explicitly "do not relax the acceptance criteria") is carried
  forward to t72 unchanged: the waiver touches only who signs Gate 3, never an
  AC, fence, replay, or digest attestation.
- README.md invariants: <=400 lines, pure ASCII, uniform CRLF, trailing CRLF,
  exactly 17 level-2 headings, all-English, no placeholder language, and the
  distinct full-form requirement-id set must not move (the 749-row coverage
  matrix scans README.md).
- `docs/state/merge_test_index.json` is orchestrator-owned; no card branch
  edits it. Pin moves happen ONLY by orchestrator append at merge, and the
  retired-pin exclusions `tests[227]` (pin-2) and `tests[231]` (pin-3) stay
  untouched.
- Carried gates are dispositioned line-by-line, never silently changed. The
  README-touching carried set at the 259-entry index is 34 entries
  (27, 119, 128, 135, 144, 149, 150, 155, 191, 196, 199, 201, 210, 227,
  231-236, 242-258); the replay set t72 inherits from t71 ac2 is the 25-entry
  set 27, 119, 128, 135, 144, 201, 232-236, 242-255 plus t71's own 256-258,
  with 227/231 as the two named retired-pin exclusions and 191 as the named
  pre-existing RED.
- Contract-first is enabled for backend/api/database and this milestone changes
  none of them: t72 is documentation + the docs verifier, t73/t74 are UI/UX,
  which `contract_first.allow_natural_for` permits.
- NO `docs/issues/<id>.md` full Gate-1 card at survey (established convention
  since t44): the three local cards carry the DEFINED-stage sections (Metadata,
  Goal, AC draft, Dependencies, Constraints, DoD template) with the rulings and
  hard constraints embedded; Context, Out of scope and the DoD specifics are
  authored at groom.
- Platform numbering: highest existing issue is #77 (closed, verified via
  `issue get 77`); #78/#79/#80 verified 404 before creation. The three cards are
  #78, #79, #80, one create call each, labels [defined] read back per issue.

## phase_13_ops_security_hardening - Operational diagnosis, observability, incident response and security-report hardening (operator directive 2026-10-16)

**Origin and scope statement (read this first).** Final Project criterion 13
(Security, Audit, DevOps hardening) currently sits at the 1-point bar: the
security scan set exists and its accepted-findings loop is closed, but the
operational half is a STATIC worked example (`ops/diagnosis.md` documents one
hand-run smoke sequence) and the two carrier directories the criterion names -
an observability stack and an incident-response record - do not exist at all
(measured at `245cd49`: `ls` shows `ops/` with 5 names and `security/` with 8
names, and there is NO `observability/` and NO `incident-response/` directory).
This milestone makes criterion 13 provably reach the 2-point bar by upgrading
that static example into an ALERT-DRIVEN, MEASURED operational loop (alert rule
-> collector -> AI responder -> resolution -> reconstruction) and by adding the
two carrier directories plus a single reviewer-facing report.

**SCOPE SUPERSESSION (explicit, and it is the reason the coverage matrix must
be re-derived rather than argued).** `docs/requirements.md` REQ-OPS-082 ("CPU,
memory, latency, error rate, connection pool, disk usage are not monitored in
MVP", Priority: Should) and REQ-OPS-083 ("Prometheus metrics, Grafana, alert on
fallback, alert on error rate, structured log export, distributed tracing",
Priority: Could) describe the MVP-scope NEGATION. This milestone is an
intentional EXTENSION beyond that MVP scope: after it merges, the sentences
"not monitored in MVP" and the "future" framing no longer describe the tree -
Prometheus + Alertmanager + Grafana exist locally, `observability/alerts.yaml`
carries a fallback alert and a business error-rate alert, and metrics/logs are
exported. The operator directive of 2026-10-16 therefore SUPERSEDES the
MVP-scope WORDING of REQ-OPS-082/083; it does not delete the REQ-IDs, does not
edit `docs/requirements.md`, and does not invent any new REQ-ID. Because the
requirement text is unchanged, the coverage matrix rows for those two REQ-IDs
are re-derived by the generator (`req_coverage_verification.py`) from the new
tree, exactly as for every other phase; NO card in this milestone may
hand-edit `docs/criteria/req_coverage_verification.md`, which is
generator-owned. `docs/criteria/security_ops_verification.md` is the criterion
13 evidence file and IS hand-maintained - t89 is its only writer in this
milestone.

**The single-authority rule that makes the 15 cards one system instead of 15
artifacts.** `observability/alerts.yaml` (t76) is the SINGLE SOURCE OF TRUTH
for every alert name and metric name used anywhere in this milestone. t79's
counter names must match it verbatim, t83's `alert.json` is a byte-copy of its
`DBFallbackActive` entry, t77's dashboard panels read its metric names, and
t85's rewritten diagnosis takes its alert name from it. No other card may
invent an alert or metric name. Likewise `incident-response/incidents/
2026-10-17-db-fallback-01/` is owned by exactly one card (t83 creates the ID
and directory, t84 fills the evidence/response/resolution trio inside it) and
README's criterion-13 row is owned by exactly one card (t89).

### Measured base state this plan relies on (commands actually run at survey, on `245cd49`)

| claim | command actually run | measured result |
|---|---|---|
| the two carrier directories do not exist | `ls` at repo root; `ls ops security` | root has `ops/` (deployment-health.md, diagnosis.md, health-check.md, logging.md, runbook.md) and `security/` (agent-security-notes.md, ai-tool-data-policy.md, gitleaks-report.json, npm-audit-report.txt, pip-audit-report.txt, pr-audit.md, semgrep-report.json, trivy-report.json); `observability` and `incident-response` -> "No such file or directory" |
| the diagnosis example is static and hand-run, and its strings are gate-pinned | `grep -n "^## " ops/diagnosis.md`; `grep -c . ops/diagnosis.md` | sections Scenario / Diagnosis Steps / Expected Output / Expected Behavior / Verification / Recovery / Findings / Lessons, 130 lines; `docs/state/merge_test_index.json` tests[16]-era t41 fences pin `^curl -fsS http://127[.]0[.]0[.]1:8137/api/v1/health`, `DIAGNOSIS_ROWS scenario=1 steps=6 output=match recovery=1 PASS`, the 7x4 runbook counts and the 17-event logging table |
| 8137 and 8001 are the two ports nothing may collide with | `grep -rn "8137" docs/criteria/security_ops_verification.md`; `grep -n "ports" -A 2 docker-compose.yml`; `grep -n "DEV_PORTS" -A 3 scripts/dev/common.ts` | `DIAGNOSIS_ENDPOINT http://127.0.0.1:8137/api/v1/health PASS` (the t41 gate's pinned local endpoint); compose maps `"8000:8000"` for the app service and 8001 is the recorded alternate Docker-stack mapping (t41 card: "port 8001 is held by the concurrent t46 Docker stack"); `DEV_PORTS = [8000, 5173]`; the t41 gate also uses `18137`-style host ports in the infra evidence, so the observability stack uses its own documented band (see the t75 pin below) |
| the fallback state the alert reads already exists in the merged API | `grep -n "fallback" backend/app/database.py`; `grep -n "fallback_active" backend/app/routers/health.py backend/app/schemas/health.py` | `FALLBACK_DATABASE_URL: Final[str] = "sqlite:///./fallback.db"`, `is_fallback()`, and health reports `fallback_active` with `status` = `"degraded"` exactly when a fallback is active - so `DBFallbackActive` can be defined against a REAL measured payload, not a hypothetical one |
| the business counters have named landing points | `grep -n "def create_expense" backend/app/services/expense_service.py`; `grep -n "def create_category" backend/app/services/category_service.py` | `create_expense` at expense_service.py:157, `create_category` at category_service.py:107 - the two paths t79 instruments, plus `backend/app/main.py` as the factory the OTel setup and `/metrics` mount ride on |
| the backend has no telemetry dependency yet | `sed -n 1,20p backend/pyproject.toml` | dependencies are fastapi/uvicorn/sqlalchemy/alembic/pydantic/pydantic-settings/python-jose/passlib/bcrypt/httpx/psycopg - NO opentelemetry package, so t78 is the only card that may add dependencies and it adds them to `backend/pyproject.toml` only |
| the five scan reports are parseable and count-pinned | `head -40 docs/criteria/security_ops_verification.md` | `SCAN_REPORT_ROWS reports=5`, `GITLEAKS_ZERO findings=0`, `REPORT_ROWS 0,32,42,3,22`, `REGISTER_COUNT_ROWS tools=5 measured=5`, `SCAN_LOOP_ROWS findings=96 registered=96 equal=true` - so a t86 refresh that changes any count MUST be re-closed by t87 against the register, and the t41 gate that re-parses the five committed reports is a carried gate t86 must disposition |
| README has 3 lines of headroom, not 100 | `wc -l README.md`; `grep -n "README_LINES\|over 500" backend/scripts/docs_verification.py` | README = 398 lines; `README_LINES = 398` and `if lines > 500: fail("README_MEASURE FAIL ... over 500")` in the docs verifier, whose `README_MEASURE PASS lines=398 digest=df1775e5...` row is a live pin. t89 therefore budgets AT MOST 3 added lines and pins `wc -l README.md` itself |
| the pipeline convention the 15 cards must mirror | `git show 985b2c9:docs/issues/t73.md`; `npx tsx scripts/platform.ts issue get 80` | survey-stage cards are DEFINED-stage stubs (Metadata / Goal / AC draft / Dependencies / Constraints / DoD template, `labels: [defined]`, `owner: definer-survey`); the ac_hash digest recipe (sha256 over the JSON-compact array of the card's fenced bash commands, CR-stripped and trimmed) is authored at GROOM (t74 groom's `ac_hash: sha256:4f3df182...`), so the survey card records the recipe and the fence-count plan instead of a digest constant |

### Milestone issue template (fifteen cards, the exact operator-approved split)

> Issue template (Batch A):
> - Requirement: criterion 13 (22.14 / 24.2 row 19) + REQ-OPS-082/083 as
>   SUPERSEDED-beyond-MVP wording (see the scope-supersession paragraph) +
>   operator directive 2026-10-16. No new REQ-ID is invented anywhere.
> - Title: t75 observability skeleton - `observability/README.md` +
>   `observability/compose.yaml` (Prometheus, Alertmanager, Grafana; OTel
>   collector / Loki / Tempo present but commented optional)
> - Acceptance: the compose file is valid YAML with exactly the three enabled
>   services and the optional block commented; the chosen host-port band is
>   documented and provably collides with NEITHER 8001 nor 8137 (nor 8000 /
>   5173 / 18137); the README states what each component does for THIS repo.
> - Files: observability/README.md, observability/compose.yaml
> - Depends: []
>
> Issue template (Batch A):
> - Requirement: criterion 13 + REQ-OPS-040..048 (diagnosis/records) extended
>   by the operator directive; REQ-OPS-082/083 superseded wording
> - Title: t80 incident-response evidence collector -
>   `incident-response/collect-evidence.sh` + `incident-response/README.md`,
>   including the `--simulate-fallback` mode that produces REAL degraded
>   evidence
> - Acceptance: the collector gathers the health payload, a `/metrics`
>   snapshot, a backend log tail and the deployed version into
>   `incidents/<ID>/evidence/`; `--simulate-fallback` points DATABASE_URL at a
>   dead PostgreSQL, restarts the local uvicorn, captures the degraded
>   evidence, and RESTORES the original state; the script is bash-clean and
>   touches no production system.
> - Files: incident-response/collect-evidence.sh, incident-response/README.md
> - Depends: []

> Issue template (Batch B):
> - Requirement: criterion 13; REQ-OPS-083's Prometheus/Grafana/alert-on-fallback
>   items, realised rather than deferred
> - Title: t76 Prometheus scrape config + the alerts authority -
>   `observability/prometheus.yml` + `observability/alerts.yaml`
> - Acceptance: `alerts.yaml` is the single source of truth and defines at
>   least `HighExpenseCreationFailures` (business metric, threshold + `for:`
>   duration + annotations service/environment/version/dashboard URL) and
>   `DBFallbackActive` (health degraded / `fallback_active` sustained 5m);
>   `prometheus.yml` scrapes the local backend `/metrics` and itself; both
>   files parse under the pinned validator.
> - Files: observability/prometheus.yml, observability/alerts.yaml
> - Depends: [t75]
>
> Issue template (Batch B):
> - Requirement: criterion 13 (AI-driven incident response); operator directive
> - Title: t81 responder prompt + response schema -
>   `incident-response/responder-task.md` +
>   `incident-response/response.schema.json` + one validator/test file
> - Acceptance: the schema is machine-validated by a PINNED command (a
>   jsonschema validation leg that is RED at base because the file does not
>   exist and GREEN once it does); the prompt states the responder's read-only
>   scope and the required output shape.
> - Files: incident-response/responder-task.md,
>   incident-response/response.schema.json,
>   incident-response/validate_response.py (validator/test leg)
> - Depends: [t80]
>
> Issue template (Batch B):
> - Requirement: criterion 13; REQ-OPS-083 metrics substrate (superseded
>   wording); REQ-TECH-020/025 for the toolchain
> - Title: t78 OTel metrics substrate (backend) -
>   `backend/app/telemetry.py` + `backend/pyproject.toml` + the app factory +
>   its test file
> - Acceptance: OTel SDK + Prometheus exporter with Resource attributes
>   `service.name` / `deployment.environment` / `service.version`; a `/metrics`
>   endpoint that is LOCAL-ONLY by a stated mechanism; the substrate is proven
>   by a backend test, not by an attestation.
> - Files: backend/app/telemetry.py, backend/pyproject.toml,
>   backend/app/main.py, backend/tests/unit/test_telemetry.py
> - Depends: []
> - HARD CONSTRAINTS recorded in the card: `openapi.yaml` is FROZEN and
>   `/metrics` is DELIBERATELY EXEMPTED from it - the exemption is recorded in
>   the card text, never by editing the contract (contract_first applies to
>   backend/api/database, and this is the one documented carve-out); the
>   local-only mechanism must be named in the card (loopback bind /
>   separate-mount gate), not implied.
>
> Issue template (Batch B):
> - Requirement: criterion 13 business signal; REQ-OPS-083 error-rate item
>   (superseded wording)
> - Title: t79 business counters - `expense_created_total`,
>   `expense_create_failures_total`, `category_created_total` on the merged
>   create paths
> - Acceptance: the three counters increment on the merged
>   `create_expense` / `create_category` service paths (including the failure
>   leg), the metric NAMES match `observability/alerts.yaml` verbatim (the
>   card proves it by extraction, not restatement), and backend tests prove
>   the increments.
> - Files: backend/app/services/expense_service.py,
>   backend/app/services/category_service.py, backend/app/telemetry.py,
>   backend/tests/unit/test_business_metrics.py
> - Depends: [t78, t76]
>
> Issue template (Batch B):
> - Requirement: criterion 13 incident record; operator directive
> - Title: t83 incidents scaffold + the incident-ID authority -
>   `incident-response/incidents/README.md` + the
>   `2026-10-17-db-fallback-01` `alert.json` + that incident's `README.md`
> - Acceptance: this card OWNS the incident-ID constant
>   `2026-10-17-db-fallback-01`; `alert.json` is a VERBATIM copy of the
>   `DBFallbackActive` entry of `observability/alerts.yaml` (proven by
>   extraction against the t76 file); the incidents README states the ID
>   grammar and the directory contract every later card obeys.
> - Files: incident-response/incidents/README.md,
>   incident-response/incidents/2026-10-17-db-fallback-01/alert.json,
>   incident-response/incidents/2026-10-17-db-fallback-01/README.md
> - Depends: [t76, t80]

> Issue template (Batch C):
> - Requirement: criterion 13; REQ-OPS-083 Grafana item (superseded wording)
> - Title: t77 dashboard + collector - `observability/dashboard.json` +
>   `observability/collector.yaml`
> - Acceptance: `dashboard.json` is valid JSON under a pinned validator and
>   carries panels for expense creation rate, creation failure rate and
>   fallback state, reading the t76 metric names; `collector.yaml` is the
>   documented optional OTel collector config.
> - Files: observability/dashboard.json, observability/collector.yaml
> - Depends: [t76]
>
> Issue template (Batch C):
> - Requirement: criterion 13 (autonomy boundary + response actions); operator
>   directive
> - Title: t82 autonomy policy + runbooks -
>   `incident-response/autonomy-policy.yaml` + `runbooks/rollback.sh` +
>   `runbooks/verify-recovery.sh`
> - Acceptance: the policy DENIES restart-of-production / DB mutation / merge
>   and ALLOWS read-only log+metric reads and report writing;
>   `verify-recovery.sh` asserts health `status ok` and `fallback_active
>   false` and exits non-zero otherwise.
> - Files: incident-response/autonomy-policy.yaml,
>   incident-response/runbooks/rollback.sh,
>   incident-response/runbooks/verify-recovery.sh
> - Depends: [t80]
>
> Issue template (Batch C):
> - Requirement: criterion 13 measured evidence; operator directive
> - Title: t84 measured drill + incident record - execute the t80 harness and
>   land `evidence.json`, `response.json`, `resolution.md` for
>   `2026-10-17-db-fallback-01`
> - Acceptance: the evidence is REAL measured degraded output from the t80
>   `--simulate-fallback` run (never attested-by-reference); `response.json`
>   validates against the t81 schema (an AI on-call pass over the evidence);
>   `resolution.md` carries the recovery-verification output and a timeline.
> - Files: incident-response/incidents/2026-10-17-db-fallback-01/evidence.json,
>   .../response.json, .../resolution.md
> - Depends: [t80, t81, t82, t83, t78, t79]

> Issue template (Batch C):
> - Requirement: criterion 13 scan currency (REQ-SEC-070/071/074 family)
> - Title: t86 scan refresh - re-run all five committed reports against the
>   final tree
> - Acceptance: `security/gitleaks-report.json`, `npm-audit-report.txt`,
>   `pip-audit-report.txt`, `semgrep-report.json`, `trivy-report.json` are
>   re-run so their timestamps and tree hash describe the merged final tree;
>   gitleaks stays measured-zero; the t41 re-parse gate and the t40
>   accepted-findings closed loop are dispositioned line-by-line.
> - Files: security/gitleaks-report.json, security/npm-audit-report.txt,
>   security/pip-audit-report.txt, security/semgrep-report.json,
>   security/trivy-report.json
> - Depends: [t84] - it MUST merge after every product-code card so the
>   reports describe the final tree.

> Issue template (Batch D):
> - Requirement: criterion 13 alert-driven diagnosis (REQ-OPS-040..048,
>   REQ-ARCH-033) + operator directive
> - Title: t85 diagnosis rewrite to alert-driven - `ops/diagnosis.md` +
>   `ops/runbook.md`
> - Acceptance: the narrative is alert-driven (alert name verbatim from
>   `observability/alerts.yaml`, proven by extraction) and points at the t84
>   measured evidence directory; the healthy-baseline smoke section and every
>   assertion string the merged t41 gate depends on stay BYTE-IDENTICAL - the
>   card is ADD-only for existing sections and pins a check that re-greps the
>   t41-pinned strings (`^curl -fsS http://127[.]0[.]0[.]1:8137/api/v1/health`,
>   `DIAGNOSIS_ROWS scenario=1 steps=6 output=match recovery=1 PASS`, the 7x4
>   runbook counts, the 17 logging events).
> - Files: ops/diagnosis.md, ops/runbook.md
> - Depends: [t84, t76]
>
> Issue template (Batch D):
> - Requirement: criterion 13 accepted-findings loop (REQ-SEC-074) +
>   REQ-OPS-083 trace limitation
> - Title: t87 accepted-findings refresh - bind the t86 findings to
>   dispositions and record traces as a documented limitation
> - Acceptance: every newly surfaced finding is bound to a disposition in
>   `security/agent-security-notes.md`; `security/ai-tool-data-policy.md`
>   records that metrics + logs are implemented while TRACES are not, as a
>   named limitation rather than a claim.
> - Files: security/agent-security-notes.md, security/ai-tool-data-policy.md
> - Depends: [t86]
>
> Issue template (Batch D):
> - Requirement: criterion 13 reviewer-facing summary (REQ-DOC-010 family)
> - Title: t88 single report - `docs/operations-and-security-report.md`
> - Acceptance: one document with PR audit summary, security scan summary,
>   agent + extension security, operational diagnosis, AI tool/data policy,
>   the incident reconstruction chain (ID -> alert -> evidence -> response ->
>   resolution -> scan finding -> disposition, each with a real file path),
>   known limitations and future improvements.
> - Files: docs/operations-and-security-report.md
> - Depends: [t85, t87]
>
> Issue template (Batch D):
> - Requirement: criterion 13 evidence map (22.14 / 24.2 row 19)
> - Title: t89 evidence map + criteria closeout - `README.md` +
>   `docs/criteria/security_ops_verification.md`
> - Acceptance: the README criterion-13 row gains the new artifacts within a
>   HARD budget of at most 3 added lines (`wc -l README.md` pinned, base 398,
>   the docs verifier's 500-line ceiling and its `README_LINES`/digest pin
>   dispositioned); the criterion-13 evidence file gains the new artifact rows.
> - Files: README.md, docs/criteria/security_ops_verification.md
> - Depends: [t88]

### Batch plan (generation discipline) and scheduling

N = 15, so `batch_size = min(5, max(1, ceil(15/3))) = 5` and
`total_batches = 3` for CARD GENERATION. The approved card list is
non-contiguous in ID space, so the batches are the operator-approved batches:

| batch | cards | written in this pass |
|---|---|---|
| A | t75, t80 | 2 cards (roots of the two carrier directories) |
| B | t76, t78, t79, t81, t83 | 5 cards |
| C | t77, t82, t84, t86 | 4 cards |
| D | t85, t87, t88, t89 | 4 cards |

Batch A is smaller than the batch cap because the approved DAG puts both
directory-creating cards first; batches C+D are 4+4 rather than 5+3 so that the
scan-refresh card (t86, which must merge LAST of the product cards) sits in the
same written batch as the drill that produces its tree, and the four
documentation-closeout cards land together. Every batch is persisted before the
next begins.

Scheduling constraints the orchestrator must honour (from the dep sets, not
invented here): t79 requires BOTH t78 and t76 merged; t84 is the widest fan-in
card in the project so far (six deps) and cannot start until t78/t79/t81/t82/
t83 have all merged; t86 must merge after every card that changes product code
(t78, t79 above all) because its reports describe the final tree; t89 is last
because it edits the pinned README row. With `MAX_SLOTS=2` the safe concurrency
is (t75, t80), then (t76, t78), then (t77, t82, t81 pairwise), then t79, t83,
t84, t86, t85, t87, t88, t89 sequentially - t85/t87/t88/t89 are a strict chain
and must never be co-scheduled with each other.

### Port allocation decision (pinned once, here, so no card invents one)

| port | owner | evidence |
|---|---|---|
| 8000 | compose app service + `npm run dev` API | `docker-compose.yml` `"8000:8000"`, `scripts/dev/common.ts` `DEV_PORTS = [8000, 5173]` |
| 5173 | vite dev | `scripts/dev/common.ts` |
| 8001 | the recorded alternate Docker-stack mapping - FORBIDDEN for this milestone | t41 card: "port 8001 is held by the concurrent t46 Docker stack" |
| 8137 | the pinned local verification endpoint - FORBIDDEN for this milestone | `DIAGNOSIS_ENDPOINT http://127.0.0.1:8137/api/v1/health PASS` |
| 9090 / 9093 / 3000 | Prometheus / Alertmanager / Grafana host bindings chosen by t75 | measured FREE at survey: `grep -rn "9090\|9093\|3000"` over `docker-compose.yml`, `render.yaml`, `scripts/dev/` returns ZERO hits, so the band is uncontested; t75 must still re-measure with `netstat -ano -p tcp` at build time and record the output |

t75 owns this band; t76/t77 reference it; no other card picks a port.

### Verification-command discipline (the t72/t73/t74 lesson, binding on groom)

- Every pinned fence must be SELF-CONTAINED. The t73/t74 ac5 legs were
  excluded from the merge index append because they pinned a moving git base
  into an appendable fence; the orchestrator recorded it in the append commits
  ("ac5 excluded - BASE-pinned quality/delta leg not append-safe").
- If a card needs a delta-purity check, the card TEXT declares the BASE-pinned
  leg non-appendable, or the purity leg is expressed against a FIXED immutable
  ref (a tagged commit or the milestone base `245cd49`), never against "main
  tip at run time".
- No fence may pin a moving count upward as its only signal (the t72
  eight-steps-to-nine lesson): where a count legitimately grows, the card
  states the new count, the carried gate that pins the old one, and the
  disposition of that gate.
- `ac_hash` is authored at GROOM with the established recipe (sha256 over the
  `JSON.stringify` array of the card's fenced bash command bodies in ac1..acN
  order with COMPACT separators, each body CR-stripped and trimmed). The
  survey card records the fence count and the recipe, never a digest constant.
- Windows discipline: git/npm/npx go through
  `cmd.exe /d /c "cd /d . && <one command>"`, one logical operation per call,
  no `/dev/null` redirection (use `nul` in cmd.exe, or no redirection at all);
  every write is verified by a separate read-back call.

### Standing constraints for every card in this milestone

- `docs/criteria/req_coverage_verification.md` is GENERATOR-OWNED: no card
  edits it. `docs/criteria/security_ops_verification.md` is hand-maintained
  and t89 is its only writer here.
- `openapi.yaml` is FROZEN for the whole milestone. `/metrics` is the one
  documented, card-text-recorded exemption (t78); no card edits the contract.
- `docs/state/merge_test_index.json` (268 entries at `245cd49`),
  `merge_history` (74 entries) and the WAL are orchestrator-owned; no card
  branch edits them, and the deferral register in the criterion-13 evidence
  file stays honest (a deferred row is never written as PASS).
- Product-code changes are confined to t78 and t79 (backend telemetry
  substrate + counters) and are ADDITIVE: no endpoint contract change, no
  schema/migration change, no behaviour change to the create paths beyond
  emitting a counter, and no change to the health payload vocabulary that the
  t41 gate cross-greps (`fallback_active`, `status`).
- Docker is used ONLY as committed configuration (t75's compose file is
  authored and validated, and the t84 drill runs against the LOCAL uvicorn on
  the pinned endpoint, not against the observability stack). No card requires
  a running Prometheus to pass its fence, and no card kills a stack it does
  not own.
- The autonomy boundary is a card, not a comment: t82's policy denies
  restart-of-production, DB mutation and merge; anything the t84 responder
  does must sit inside the allowed set, and `resolution.md` must show the
  verification leg rather than assert recovery.
- README.md is reviewer-owned by `docs/ownership.md`; the phase_11 HUMAN-REVIEW
  RULING carries forward (per-card approval waived, replaced by a mandatory
  rigorous orchestrator pre-merge re-check; no AC, fence, replay or digest
  attestation is relaxed). t89's 3-line budget is the operative constraint.
- Cards follow the phase_12 pipeline convention: survey writes DEFINED-stage
  stubs (Metadata, Goal, AC draft, Dependencies, Constraints, DoD template)
  with the rulings and hard constraints embedded; Context, Out of scope, the
  fenced ACs and the `ac_hash` are authored at groom.
- Granularity: max_files=4, max_acs=6, max_diff_lines=300 (warn-only, per
  `docs/config.yaml` via the factpack `config_subset`). Every card is at most
  FIVE ACs and at most FOUR files EXCEPT ONE DISCLOSED EXCEPTION: t86 names
  FIVE files (the five scan reports). The exception is deliberate and is the
  operator-approved split - the five reports MUST be refreshed by a single card
  in a single run or they describe five different trees, which is exactly the
  currency claim the criterion asks for; splitting them into two cards would
  trade a warn-only limit for a false evidence statement. `within_limits` is
  therefore reported FALSE in the survey handoff (honest, not rounded up), the
  limit is `warn_only: true`, and no other card in the milestone exceeds four
  files. t86's five files are machine-generated report output, not hand-written
  code, and its diff-line count is disclosed as expected-over-cap for the
  report bodies.

## phase_14_render_live_closeout - Render go-live closeout: gate re-premise, live-URL backfill, evidence and the two README fixes (operator-approved audit, WAL 1098)

**Origin and scope statement (read this first).** The app is LIVE. Measured by
the operator and recorded in the factpack `orchestrator_context.live_state`:
`https://expense-tracker-dashboard-1qtu.onrender.com/api/v1/health` answers
`200 {"status":"ok","database":"postgresql","fallback_active":false,
"version":"0.1.0"}`, the old no-suffix URL answers `404`, both GitHub secrets
(`RENDER_DEPLOY_HOOK`, `RENDER_APP_URL`) exist, the UptimeRobot monitor is
green on the `-1qtu` URL, and `main` == `origin/main` == `890680e`. What is
missing is not a feature but the CLOSEOUT: seven gaps (G1-G7 in the factpack)
where the tree still describes a deployment that has not happened, plus one
uncommitted operator edit to `.github/workflows/deploy.yml` that a stored gate
currently rejects. This milestone closes exactly those gaps. It adds NO new
feature, NO new endpoint, NO new dependency, NO new REQ-ID, and it does not
reopen, close or edit any pre-existing platform issue except #61 (t95's single
sanctioned close).

**Nine cards, the operator-approved split, and the issue map.** The approved
audit named eight cards (A1, A2, A3, B1, B2, B3, C, D). B1 is split at survey
into B1a/B1b under the mid-run register recon
(`orchestrator_context.b1_register_recon`: "the Orchestrator accepts the
split"), so this milestone DEFINES NINE cards. CARD-ID MAPPING, stated once
because the letters and the ids differ: B1a is card **t93** (platform #99)
and B1b is card **t98** (platform #100) - the ids are `t93`/`t98` rather than
`t93a`/`t93b` because `schemas/definer/survey.json` and
`schemas/state/milestone.json` both constrain an issue id to `^t[0-9]+$`, so a
letter-suffixed id would be schema-invalid in the handoff and the milestone
record; `t93` was free (the audit's B1 slot) and `t98` is the next free id
above t97. The nine cards are therefore t90, t91, t92, t93, t98, t94, t95, t96,
t97, and the card letters (A1, A2, A3, B1a, B1b, B2, B3, C, D) keep the
operator's naming so the audit trail stays one-to-one.

| card | issue | one-line definition | depends |
|---|---|---|---|
| A1 | t90 | Formal gate amendment for `docs/state/merge_test_index.json` tests[133] (t26), RE-PREMISE not relax, plus the builder commits the operator's `deploy.yml` edit | [] |
| A2 | t91 | `render.yaml` `CORS_ORIGINS` moves to the real `-1qtu` domain as a quoted JSON array; `APP_VERSION` stays the quoted string `"1.0.0"`; tests[134] re-runs GREEN | [] |
| A3 | t92 | Real `workflow_run` green evidence (run id + the `deploy verified: health endpoint is ok` log line + Render build/migration logs) closing the REQ-CICD-034 final-step gap | [t90, t91] |
| B1a | t93 | The `security_ops` half of the live-state move: `RENDER_HEALTH_PATH` (`security_ops_verification.py:62`) moves to the `-1qtu` host, `LIVE_DEPLOYMENT_STATE` leaves the deferral register as a VERIFIED row, the literal header at `:568` moves `5 DEFERRED -> 4 DEFERRED`, the criteria report is REGENERATED, and `ops/deployment-health.md` + `ops/diagnosis.md` prose moves NOT_YET_LIVE/404 -> live with the UptimeRobot confirmation and the free-tier 30-day inactivity note. Carries the tests[187] re-premise (count AND the old-URL/404-reason row text) | [t92] |
| B1b | t98 | The `docs`/`infra` half: the `docs_verification.py:416` register list drops `LIVE_DEPLOYMENT_STATE` (the emitted count at `:448` is DERIVED from the list length, so `4 DEFERRED -> 3 DEFERRED` follows), the `:422` live_check URL moves to `-1qtu`, `infra_verification.py:602` moves, both criteria reports are REGENERATED, and the tests[219]/[223]/[226] register-count pins are re-premised as verified-row assertions | [t92, t93] |
| B2 | t94 | README `## Online demo` and `## Deployment on Render` backfill the real URL, with the README triple-pin moved in the SAME card, and the honest statement that the hosted app has NO seeded demo account | [t98] |
| B3 | t95 | Close platform issue #61 with the A3 + B1a + B1b + B2 evidence bundled | [t92, t93, t98, t94] |
| C | t96 | Remove README Quick Start step 3 (`cp .env.example .env`, README:94-95) and re-premise tests[232] plus the tests[251] sabotage victim; the README:340 copy STAYS (REQ-DOC-071 mandated, tests[201]/tests[255]) | [] |
| D | t97 | Health version single source: `backend/app/main.py:81` builds `FastAPI(..., version=settings.APP_VERSION)` so the live `/api/v1/health` reports `1.0.0` | [] |

**Why B1 is two cards and not one (measured, not invented).** The approved B1
brief read as a URL-constant patch. The register recon measured it as a
generator-and-gate migration: `security_ops_verification.py:568` appends the
LITERAL `"DEFERRAL_REGISTER 5 DEFERRED"`, `docs_verification.py:416` builds a
list whose length `:448` emits (the docs-side count is DERIVED, not literal),
`docs/criteria/*.md` are GENERATED artifacts a builder regenerates and never
hand-edits, and the counts are pinned verbatim by stored gates - tests[187]
pins `^DEFERRAL_REGISTER 5 DEFERRED$`, a `DEFERRED_ROW` count of 5 AND the
whole `LIVE_DEPLOYMENT_STATE` row text including
`reason=live_render_url_returns_404_measured` and the OLD no-suffix
`https://expense-tracker-dashboard.onrender.com/api/v1/health`; tests[219],
tests[223] and tests[226] each pin `DEFERRAL_REGISTER 4 DEFERRED` in
`docs/criteria/docs_verification.md` (tests[226] in prose: "the register must
stay at 4 DEFERRED"). One card doing both halves would own five authored files
across two generators plus three regenerated reports and two separate
gate-amendment sets; splitting on the generator boundary gives two cards inside
`max_files=4` with one amendment set each, and the split point is exactly where
the write ownership already falls.

**Batch plan (batch_size = min(5, max(1, ceil(9/3))) = 3; three batches).**

| batch | cards | why this grouping |
|---|---|---|
| 1 | t90, t91, t92 | The two gate/config cards and the evidence card that consumes both. t92 is written in batch 1 but CANNOT START until t90 and t91 have merged and been pushed - its dep set says so and the push/wait is real wall-clock, not a formality. |
| 2 | t93, t98, t94 | The live-state backfill: the `security_ops` generator + ops record, then the `docs`/`infra` generator half with its three register pins, then the README. t98 follows t93 because both move the same `LIVE_DEPLOYMENT_STATE` row and t93 lands the verified-row pattern t98 reuses. |
| 3 | t95, t96, t97 | The residual close (which consumes batch 2) plus the two independent fixes, both `depends: []`, safe to co-schedule under `MAX_SLOTS=2`. |

**Scheduling constraints the orchestrator must honour.**

- t92 is the only card in the project with an EXTERNAL precondition: a real push
  to `main`, a real E2E `workflow_run` completion, the deploy job firing, and
  Render build/migration logs. It cannot be simulated; a fabricated run id is a
  FAIL, not a shortcut.
- t93 merges after t92 because its `ops/deployment-health.md` evidence IS the
  A3 capture. t98 after t93 (shared row, shared pattern). t94 after t98
  because the README cites the state the registers record. t95 last because it
  bundles all of them.
- **README single-writer rule:** README.md is touched by exactly TWO cards, t94
  and t96, and they must NEVER be co-scheduled or merged in one window. Both
  move the README triple-pin; two writers in one window is how a pin-custody
  dispute (the tests[259] `pin custody moves ONLY by orchestrator append at
  merge` leg) is born. Order: t94 first, t96 after.
- **`docs_verification.py` is a three-writer file, sequential:** t98 (register
  list + live_check), then t94 (README pin constants), then t96 (README pin
  constants + the tests[251] re-premise). Never concurrent, never in one window.
- Gate amendments are applied by the ORCHESTRATOR in the strict merge window,
  never by a builder, a verifier, or the definer. The definer authors the
  amendment RECORD only, on the t89 precedent
  (`docs/state/outputs/t89_definer_gate_amendment.json`). That covers t90
  (tests[133]), t93 (tests[187] and any consistency leg that flips), t98
  (tests[219]/[223]/[226]) and t96 (tests[232], tests[251], and any flip-set
  member groom measures).
- t97 is backend product code; t96 is README plus stored-gate re-premises.
  Neither interacts with batch 1/2 beyond the shared file noted above.

**Shared-file ownership (one writer per file, per merge window).**

| file | owner | note |
|---|---|---|
| `.github/workflows/deploy.yml` | t90 only | The builder commits the operator edit byte-identical to the diff the factpack records. No other card touches `.github/**`. |
| `render.yaml` | t91 only | tests[134] is RE-RUN, never amended. |
| `docs/state/merge_test_index.json` | ORCHESTRATOR only | t90 / t93 / t98 / t96 each hand over an amendment RECORD; none edits the file. |
| `backend/scripts/security_ops_verification.py` | t93 only | |
| `backend/scripts/infra_verification.py` | t98 only | |
| `backend/scripts/docs_verification.py` | t98, then t94, then t96 | Sequential; see the three-writer rule above. |
| `ops/deployment-health.md`, `ops/diagnosis.md` | t93 only | |
| `docs/criteria/*.md` | GENERATOR only | Regenerated by RUNNING the owning generator. t93 owns the `security_ops` report; t98 the `docs` and `infra` reports; t94/t96 the `docs` report through the generator only. No card hand-edits a criteria report. |
| `README.md` | t94 then t96, never concurrently | The triple pin moves with each edit. |
| `backend/app/main.py` | t97 only | |
| platform issue #61 | t95 only | The only pre-existing issue any card may close. |

**Measured base state this plan relies on.** Every value is consumed from the
factpack (`orchestrator_measured_recon`, `b1_register_recon`, `c_d_recon`; WAL
1099 and later: "DO NOT RE-MEASURE"), plus phase_13-era measurements already on
the record. Where a value was NOT measured by anyone, the row says ASSUMED and
the owning card's Constraints repeat it as a groom-time measurement.

| claim | source | value |
|---|---|---|
| the gate index is append-only and identity-pinned | recon `index` | 318 entries in `tests[]`, identity = index + `issue_id` |
| tests[133] (t26) is RED on exactly one leg | recon `tests_133` | `RENDER_DEPLOY_HOOK must be the ONLY secret referenced, got RENDER_DEPLOY_HOOK,RENDER_APP_URL`; every other leg (hook secret present, no `api.render.com/deploy/` literal, `-X POST`, `seq 1`, `sleep`, `exit 1`, `/api/v1/health`, >=2 steps, all e2e.yml legs) measured GREEN |
| the amendment target | recon `tests_133.amendment_target` | Replace ONLY the single-secret assertion with a CLOSED allowlist `{RENDER_DEPLOY_HOOK (hook step), RENDER_APP_URL (health-verify step)}`; every other leg byte-identical; a third distinct secret must still turn it RED (negative control) |
| the operator edit | recon `operator_deploy_yml_diff` | health-verify step gains `env: APP_HEALTH_URL: ${{ secrets.RENDER_APP_URL }}`, the curl line becomes `curl -fsS "$APP_HEALTH_URL"`; `deploy.yml` then references exactly 2 secrets |
| tests[134] stays GREEN on a corrected CORS value | recon `tests_134.cors_leg` | `String(ev.CORS_ORIGINS.value).indexOf("onrender.com")>=0` - a substring test, so `-1qtu` passes |
| tests[134] APP_VERSION leg | recon `tests_134.app_version_leg` | `String(ev.APP_VERSION.value)==="1.0.0"` - unquoted `1.0.0` parses to the float `1.0` and FAILS; the value must stay a quoted string |
| the README pin surface | recon `readme_pin_indices` | [227, 232, 243, 250, 251, 252, 255, 201]; 227 is the t59 digest pin (already RED, parked under U5), 232 is the `cp .env.example .env` Quick Start gate card C re-premises, 243 is the section-heading gate that must stay GREEN across C and B2, 250/251/252 are the t69 gates, 255 is the `## Deployment on Render` heading gate B2 must keep, 201 is the t49 copy gate mandating the README:340 text card C must NOT delete |
| the env-copy token appears TWICE | `c_d_recon` | README:94-95 (Quick Start step 3, to be deleted by C) AND README:340 inside `## Deployment on Render` (MUST STAY - REQ-DOC-071 mandated, pinned by tests[201] and tests[255]) |
| tests[27] must not be relaxed | `c_d_recon` | tests[27] (t4) is an UNanchored grep and stays GREEN through README:340 - C proves it GREEN, it does not amend it |
| tests[251] needs a victim redefinition | `c_d_recon` | tests[251] (t69 ac2) is a sabotage-based carried-gate replay whose victim is "the env-file copy line"; once step 3 is gone, sabotaging that line may no longer turn tests[27] RED, so the victim moves to the README:340 copy in the SAME card |
| the three URL constants | `script_url_constants` + `b1_register_recon` | `security_ops_verification.py:62 RENDER_HEALTH_PATH`, `docs_verification.py:422 live_check`, `infra_verification.py:602`; plus `ops/deployment-health.md:56` (CORS_ORIGINS deviation row quotes the old domain) and `ops/diagnosis.md:8` (deployed-endpoint prose) |
| the register counts are hardcoded and pinned | `b1_register_recon` | `security_ops_verification.py:568` literal; `docs_verification.py:416`/`:448` derived; pinned by tests[187] (count + row text + old URL), tests[183]/[184]/[185] (generator/criteria consistency), tests[219], [223], [226] |
| the deferral registers today | measured at survey by `grep -n "^DEFERRAL_REGISTER" docs/criteria/*.md` | `security_ops_verification.md:83 = 5 DEFERRED`, `docs_verification.md:33 = 4 DEFERRED`, `infra_verification.md:83 = 7 DEFERRED`, `agent_pack_verification.md:98 = 3 DEFERRED` |
| the version drift is real and unpinned | survey grep + `c_d_recon` | `backend/app/main.py:81` is `FastAPI(title="Expense Tracker Dashboard API", version="0.1.0")`; `backend/app/config.py:43 APP_VERSION: str = "1.0.0"` is read only by `backend/app/telemetry.py:131`; `grep -rn "0\.1\.0" backend/tests` returns ZERO hits and no stored gate asserts the health version value, so t97 has no gate to amend - only not to break |
| the README is at its ceiling | survey measurement + phase_13 plan | README.md = 398 lines, 17 level-2 headings, CRLF on every line, ASCII-only; `docs_verification.py` carries `README_DIGEST = "ca9343a8..."`, `README_LINES = 398`, and fails on `lines > 500` |

**The triple-pin move, stated once, binding on t94 and t96.** A README edit is
legal in this milestone only if the SAME card moves all three members: (1)
`README_DIGEST`/`README_LINES` in `backend/scripts/docs_verification.py`, (2)
the regenerated `README_MEASURE PASS lines=... digest=...` row in
`docs/criteria/docs_verification.md` produced by RUNNING that generator, and (3)
the stored gates that compare them (recon set 227/232/243/250/251/252/255/201,
plus the tests[258] constant-comparison and tests[259] pin-custody legs measured
GREEN/RED respectively at survey). A card that edits README and leaves a member
behind is a FAIL, not a follow-up. Which members actually flip is a per-edit
property: groom re-measures the flip set per card by EXECUTING the stored
README-scoped gates read-only against the candidate tree (a command execution,
not a repo copy - the survey's copy-based flip probe was abandoned as unsafe and
nothing here relies on it), and every card says "groom re-measures", never
"survey proved".

**Parked by operator decision U5 - out of scope, recorded so no card drifts.**
The pre-existing RED pairs tests[161]/[162]/[191]/[227] (milestone-pin
rotation), the tests[220] known defect (`[:3]`-truncated `os.walk`), the five
older follow-up cards (t80 harness-metrics URL `collect-evidence.sh:186`, t86
AC2 wording, t84 ac3 prose, the semgrep Makefile pin, builder-task wording),
the 35 ruff UP031 findings and the 2-3 flaky backend env tests. No phase_14 card
may "helpfully" fix a parked item; a card whose diff touches a parked surface is
a FAIL. tests[227] being already RED matters only in that a card must not claim
to have made it GREEN - the digest pin still moves in the same card as any
README edit.

**Hard constraints carried into every card (factpack `hard_constraints`).** The
README is triple-pinned at 398 lines / digest `ca9343a8`; `openapi.yaml` is
FROZEN; a stored gate that greps a product file pins a literal, and changing
that literal requires a FORMAL gate-amendment card that RE-PREMISES (never
relaxes) the rule; `MAX_SLOTS=2` (`.env MAX_SLOTS=2` overrides `config
slots.max=3`); the orchestrator never writes code or edits issues, and all
platform operations go through `scripts/platform.ts`.

**Granularity.** `max_files=4`, `max_acs=6`, `max_diff_lines=300`
(`docs/config.yaml`, warn-only). All nine cards are inside `max_files` and
`max_acs` as authored files. TWO DISCLOSED EXCEPTIONS, both on the regenerated
artifacts the register/README moves force:

- Counting convention used here: AUTHORED = a file the builder writes;
  DELTA PATH = anything in the diff, including a generator-REGENERATED
  criteria report and the card's gate-amendment record. `max_files=4` is a
  cap on authored files; the regenerated reports are disclosed separately
  because no card may hand-edit them.
- **t93**: 4 authored (`security_ops_verification.py`,
  `ops/deployment-health.md`, `ops/diagnosis.md`, the amendment record) - at
  cap; 5 delta paths with the REGENERATED
  `docs/criteria/security_ops_verification.md`.
- **t98**: 3 authored (`docs_verification.py`, `infra_verification.py`, the
  amendment record); 5 delta paths with the REGENERATED
  `docs/criteria/docs_verification.md` and `infra_verification.md`.
- **t94 / t96**: 3 authored each (`README.md`, `docs_verification.py`, the
  amendment record); 4 delta paths each with the REGENERATED
  `docs/criteria/docs_verification.md`.
- **t90 / t91 / t92 / t95 / t97**: 1-2 authored files, well inside the cap.
- Diff lines: t90, t93, t98, t96 and t97 are modest. t92 and t94 are
  disclosed as likely-over-cap for the same reason t86/t88 were in phase_13:
  an evidence capture and a README backfill are prose bodies, not patches.
  `within_limits` is therefore reported FALSE in this handoff, honestly, with
  the exceedance named per card; the limit is `warn_only: true`, and the same
  shape was operator-approved in phase_13.

**Verification-command discipline (unchanged from phase_13, binding on groom).**
Every pinned fence is self-contained; a delta-purity leg is expressed against a
FIXED immutable ref (the milestone base `890680e`), never "main tip at run
time"; no fence pins a moving count upward as its only signal; `ac_hash` is
authored at GROOM by the established recipe (sha256 over the JSON-compact array
of the card's fenced bash bodies in ac1..acN order, CR-stripped and trimmed) and
the survey card records the fence count and the recipe, never a digest constant;
every git/npm/npx call goes through `cmd.exe /d /c "cd /d . && <one command>"`,
one logical operation per call, no `/dev/null` redirection, and every write is
verified by a separate read-back.

**Pipeline convention.** Survey writes DEFINED-stage stubs (Metadata, Goal,
Measured base state, AC draft, Dependencies, Constraints, DoD template) with the
rulings and hard constraints embedded; Context, Out of scope, the fenced ACs and
the `ac_hash` are authored at groom. No survey AC draft is fenced and no survey
card claims a digest.


## phase_15_gate_amendments - Gate-premise amendments: the anchor[133] refresh debt and the t95 option-A premise defects (operator authorization, WAL 1201)

**Origin and scope statement (read this first).** Phase_14 closed with all nine
cards (t90-t98) merged and closed, and with two classes of work deliberately
DEFERRED rather than silently absorbed. Both are now operator-authorized
follow-ups, and both are gate-premise work, not feature work. (1) The
**anchor[133] refresh debt**: the t90 amendment rewrote the stored command of
`docs/state/merge_test_index.json` tests[133] (the e2e/deploy workflow-structure
gate), which changed that entry's canonical JSON and therefore its `entry_sha`.
The old digest `6e9723e8…` survived in two other stored legs (tests[190],
tests[191], both t47) and in the in-repo verifier
(`backend/scripts/docs_verification.py:46`), so the tree has carried a gate that
asserts a value the index no longer contains ever since t90 - disclosed on every
merge since, and surfaced as the leg-258 GREEN->RED neighbourhood flip at t98.
(2) The **t95 option-A premise defects**: t95 shipped COMPLETE under the
operator-sanctioned option-A ruling with three independently-measured premise
defects that made its own fences ac5/ac6 RED at merge (WAL 1191, re-measured at
WAL 1195, confirmed at the merge verdict WAL 1198) - B1 the leg-214 gate matrix
that premised build-directory pollution as a product RED although 214 is GREEN on
a clean checkout, B2 the sweep runner's `node_modules` allowlist omission that
lets copy/junction-class dirt reach verification legs, and B3 the leg-255
as-stored pin that pinned t94's PRE-amendment triple `9aac9f0c/487b30e2/7945`
while the shipped index says `f5aafe07…/1878e29d…/7760`.

This milestone adds NO feature, NO endpoint, NO dependency and NO new REQ-ID. It
touches no closed card, no WAL entry, no pre-existing platform issue, and it does
not edit `docs/state/merge_test_index.json` - that file is orchestrator-owned
(pretty, CRLF, in-place amend only) and builder cards deliver **amendment
RECORDS** the orchestrator applies in the strict merge window (t89/t90/t94/t96
precedent).

**NEW BASELINE, binding on every card in this milestone.** Since the t96 verdict
(WAL 1193) the frozen RED set is **33 legs**, not 36: frozen36 MINUS {250, 254,
257} = {139,140,161,162,163,164,166,167,174,175,177,180,181,188,190,191,192,204,
216,227,230,231,258,259,272,274,275,276,289,290,294,296,309}. All re-premise
arithmetic in this milestone uses 33. Two pollution classes are known and must
never be premised as product REDs: tests[217] is RED when `.env` is present in
the checkout (`.env` is quarantined at `scratch/env_quarantine_t94post` and
removed immediately after every platform call), and tests[214] is RED under
`build/`-directory or card-location pollution while GREEN on a clean checkout.

**Four cards, and why four (the granularity call is the Definer's, per the
operator's explicit instruction to evaluate whether to split finer).** The
operator authorized the two workstreams and delegated the split. The survey
decision is **N = 4**, split by *deliverable and file ownership*, not by defect
label:

- **t99 (#105)** - the INDEX side of the anchor debt: one coordinated amendment
  RECORD for tests[190] and tests[191], the two legs that embed the stale
  `6e9723e8…` byte-pin of tests[133]. Delivered as
  `docs/state/outputs/t99_definer_gate_amendment.json` for the orchestrator to
  apply in the merge window. Predicted baseline effect ZERO - neither leg goes
  GREEN, each is RED for its own unrelated pre-existing reason.
- **t100 (#106)** - the GENERATOR side: `docs_verification.py`'s own
  `INDEX_ANCHORS[133]` constant, plus regeneration of the committed report. This
  is a product-code edit in a different file with a different verification
  surface, and it is the only card in the milestone with a predicted baseline
  change (33 -> 32: leg 258 recovers, leg 259 named retired). Depends t99, so the
  index stops asserting the old digest before the generator stops asserting it.
- **t101 (#107)** - the t95 fence-premise family (B1 + B3) as one
  premise-correction RECORD. B1 and B3 are the same defect family: two wrong
  expectations inside ONE t95 fence artifact (ac5's expectation list, ac6's
  as-stored pin table). Splitting them into two cards would force two separate
  re-grooms/ac_hash passes over the same one closed artifact for no added
  observability; per-defect rigor is preserved by separate ACs and a per-defect
  record entry, not by separate cards.
- **t102 (#108)** - B2 as its own card, because its deliverable is a DIFFERENT
  class: not a t95 fence premise but a pollution-boundary change to the
  in-repo verifier (`SKIP_DIRS` += `build`, `scratch`) plus a recorded discipline
  for the orchestrator-side sweep tooling, which is not a repo artifact and is
  therefore not patchable by any card in this repo.

Splitting further was considered and rejected on measurement: the anchor debt is
NOT one family (index literal vs generator constant - different files, different
delivery mechanisms, different baseline effects, so they are two cards, not one),
and it is NOT finer than two (both halves are single-literal substitutions with a
single measurable each). B1+B3 are one fence artifact's two premises. B2 is a
third deliverable class. Four is where the deliverables actually change.

**Single-writer rule.** t100 and t102 both edit
`backend/scripts/docs_verification.py` and both regenerate
`docs/criteria/docs_verification.md`. They must never be co-scheduled; t102
depends on t100. The DAG is therefore t99 -> t100 -> t102 with t101 an
independent root, and t99 -> nothing else: no other card depends on the index
record's landing to be verifiable.

**Measured hazards this survey recorded for groom (all re-measured at groom, not
inherited).** (a) Running `docs_verification.py` on a checkout that contains
`build/`/`scratch/` payloads produced `LINK_CHECK FAIL broken=14` with EVERY
break inside a copied tree (`build/t76/repo/…`, `scratch/t95pm/*/…`), lost the
`OPENAPI_PARITY` line, and flipped the footer `CHECKS_FAILED 1` -> `3`; the
committed report on a clean tree says `LINK_CHECK PASS files=261 links=67
broken=0` and `git ls-files '*.md'` = 261, while the walk sees 2116 `*.md` with
the current `SKIP_DIRS` and 265 once `build`/`scratch` are excluded. That is B2
reproduced, and it is why t102 exists. (b) `scratch/` is NOT gitignored while
`build/` is (`.gitignore:185`), so scratch dirt is invisible to ignore-based
reasoning but fully visible to any tree walk; making `scratch/` gitignored is a
separate operator decision and deliberately OUT of t102's scope. (c) The
generator's `STORED-GATES` legs (134/155) need `jsdom`; under WSL's system node
v18.19.1 they FAIL and the footer reads `CHECKS_FAILED 3`, while on the canonical
host (native node v24.16.0 via cmd.exe) they PASS 4/4. That is a THIRD
environment class, newly disclosed here: every rc claim in this milestone is made
on the canonical host and a WSL-node artifact is disclosed, never reported as a
product RED. (d) No stored leg pins the `files=`/`links=` counters, the
`docs_verification.py` digest, or the `entry_sha` of legs {133,190,191,204,216}
at any prefix length - the survey scanned all 318 commands - so the re-premise
surface is exactly what these four cards name.

**Verification-command discipline (unchanged, binding on groom).** Every pinned
fence is self-contained; a delta-purity leg is expressed against a FIXED
immutable ref (the milestone base `06be1e1`), never "main tip at run time"; no
fence pins a moving count upward as its only signal; every negative control must
be EXECUTED, because a re-premise that cannot fail is a relaxation and this
milestone's whole purpose is re-premise-not-relax; `ac_hash` is authored at GROOM
by the established recipe (sha256 over the JSON-compact array of the card's
fenced bash bodies in ac1..acN order, CR-stripped and trimmed) and the survey
card records the fence count and the recipe, never a digest constant; every
git/npm/npx call goes through `cmd.exe /d /c "cd /d . && <one command>"`, one
logical operation per call, and every write is verified by a separate read-back.

**Pipeline convention.** Survey wrote DEFINED-stage stubs (Metadata, Goal,
Measured base state, AC draft, Dependencies, Constraints, DoD template) with the
rulings and hard constraints embedded; Context, Out of scope, the fenced ACs and
the `ac_hash` are authored at groom. No survey AC draft is fenced and no survey
card claims a digest.

## phase_16_hygiene_staleness - Criteria-docs staleness and repo hygiene (operator directive, WAL 1230/1231)

**Scope ruling (operator, WAL 1230/1231).** TWO SEPARATE CARDS, deliberately NOT
merged: t103 regenerates the two stale generator-owned criteria documents
(`docs/criteria/agent_pack_verification.md`, `docs/criteria/req_coverage_verification.md`,
stale since the t35 era per WAL 1228); t104 executes the operator-approved hygiene
batch (`.gitignore` gains `scratch/`, the WSL/cmd.exe environment rules move into
`docs/commands.md`, and the all-leg literal `docs/issues/tXX.md` path-pin audit ships
as a checker plus a written finding). They share no path and each freezes the
other's surface.

> - t103 - Requirement: existing report-family anchors only (REQ-PLAN-061,
>   REQ-EXT-070/071/072, the t57/t58 matrix family); no new REQ-ID.
>   Title: regenerate the two stale criteria documents from their own generators,
>   with the stored-leg hazard derived and replayed rather than quoted.
>   Acceptance: committed bytes reproduce from the generators; the collection count
>   in the agent-pack doc equals a live-derived count; the matrix is self-consistent
>   and fail-closed GREEN; the derived anchored-pattern hazard replay over the
>   index legs that name these two documents passes; frozen neighbours untouched;
>   delta pure against a run-time-derived base and groom-reproducible.
>   Files: `docs/criteria/agent_pack_verification.md`,
>   `docs/criteria/req_coverage_verification.md`. Depends: [].
> - t104 - Requirement: existing repo-hygiene/commands-doc anchors only; no new
>   REQ-ID. Title: gitignore `scratch/`, codify the cmd.exe-vs-WSL environment
>   rules in `docs/commands.md`, and ship the leg path-pin audit as a checker plus
>   findings (index never patched).
>   Acceptance: `scratch/` ignored with the one tracked file's disposition executed;
>   the three env rules present additively with the stored line floor derived from
>   the index; the checker runs GREEN and demonstrably REDs on a planted break; the
>   findings record documents legs 230/279 and the t78 exemption; the index and all
>   frozen neighbours are byte-identical; delta pure against a run-time-derived
>   base and groom-reproducible.
>   Files: `.gitignore`, `docs/commands.md`, `docs/tools/` (checker),
>   `docs/state/outputs/` (findings). Depends: [].

**Hard rules inherited by both cards (phase_15 closeout findings, WAL 1221/1222).**
Delta-purity fences DERIVE their base from the branch parent at run time (`HEAD^`,
with the disclosed `merge-base`-with-main fallback, printing which base was used);
pinning BASE to a main-tip-at-groom literal is an ANTI-PATTERN that cost a full
amendment cycle on t102. The ALLOWED set names the card's own required handoff
artifacts explicitly (`docs/state/outputs/t103_builder_build.json`,
`docs/state/outputs/t104_builder_build.json`, ...) and `docs/log/orchestrator_wal.jsonl`
is deliberately EXCLUDED. `ac_hash` is authored at groom by the t58 recipe (sha256
over the JSON-compact array of the six fenced bash bodies in ac1..ac6 order,
CR-stripped and trimmed), the handoff's `verification_commands` are BYTE-IDENTICAL
to the card's fences, and every card must BITE: each fence REDs on a plausible
violation, verified in a throwaway clone BEFORE landing.

**Deliberate non-coverage.** `docs/state/merge_test_index.json` is
orchestrator-owned: neither card amends a stored leg, and both deliver recorded
findings on the t96/t99 coordinated-amendment route instead. Leg 217's
matrix-drift RED may recover as a side effect of t103, but that recovery is
measured by the orchestrator's sweep, never claimed by a card fence. `scratch/`'s
untracked mass is the subject of t104(a), not a product RED.

## phase_17_pin_repremise_checker_decode - Index re-premise for the base64-hidden card-path pins, and the checker upgrade that sees them (operator authorization, WAL 1240/1241)

**Scope ruling (operator, WAL 1241).** TWO SEPARATE CARDS, deliberately NOT merged
("分開開卡", 2026-10-21). The phase exists because the phase_16 hygiene batch moved the
archived cards to `docs/issues/closed/` and eleven legs of
`docs/state/merge_test_index.json` still name the OLD live paths from INSIDE
base64-encoded probe payloads - a class the shipped plaintext-only auditor cannot see
(WAL 1236). t105 re-premises those eleven legs (the first non-orchestrator write to the
index, authorized IN WRITING for THIS CARD ONLY); t106 upgrades the auditor so the same
class is visible next time. They share NO path and each freezes the other's surface, so
either merge order works.

**Measured base state this plan relies on (commands actually run at survey/groom).**
- The index carries 318 legs (blob 1,303,989 bytes LF; worktree 1,305,446 bytes CRLF
  under `core.autocrlf=true`, so every byte comparison in both cards is line-ending
  agnostic), `schema_version` `1.0`, `updated_at` `2026-10-19T03:00:00Z`, indent 2.
- 43 quoted base64 chunks across 34 legs, all canonical. Decoding them yields EXACTLY 11
  legs with live card paths: 282 (t76 ac4), 306/307/308/309 (t86 ac1/ac2/ac3/ac4),
  310/311/312 (t87 ac1/ac2/ac3), 315/316/317 (t88 ac1/ac2/ac3). Together with the two
  plaintext pins (230 t62 ac6, 279 t78 ac4) the pinned class is 13 legs.
- Baseline rc measured at groom: RED = {282, 308, 309} (their probes hard-fail on the
  missing card); the other eight are GREEN only because their probes never read the
  card at all. Liveness was MEASURED, not assumed: 282/308/309 read the card
  with live commands, while the other eight define card-path constants that the decoded
  payload never uses again (0 uses beyond the definition).
- No stored leg runs `docs/tools/leg_path_pin_audit.py`, so t106's upgrade changes no
  stored leg's rc.

**Numbering convention (WAL 1240 W2, binding on both cards and on every artifact of this
phase).** All leg numbers in this phase are 0-BASED ARRAY INDICES into
`merge_test_index.json`'s `legs` array, and are written WITH their `issue_id` and `ac`
attached (e.g. `tests[308] t86-ac3`), never as bare numbers - the orchestrator's sweep
runner prints 1-BASED ordinals, so a bare number is ambiguous by construction.

> - t105 - Requirement: existing verification-report/anchor family only (the t58/t63/t71
>   family that the index-leg anchors already carry, plus the t96/t99/t100 coordinated
>   amendment precedent); no new REQ-ID.
>   Title: index re-premise for the 11 base64-hidden card-path pins, delivered as a
>   WRITTEN amendment of index ownership.
>   Acceptance: the amendment is written in the card text and the derived leg set matches
>   it exactly; ONLY the 11 named legs' `command` strings change and every other leg is
>   byte-identical under canonical serialization with the key order disclosed; each edited
>   payload is re-encoded byte-disciplined (decoded diff shown, re-encoded payload decodes
>   back byte-equal); the amended index self-loads with 318 legs and unchanged
>   `schema_version`/`updated_at`; a per-leg decision record states disposition
>   disposition pair read_closed for the 3 live readers (legs 282, 308, 309) vs guard_correct_semantics for the 8 dead-constant legs (legs 306, 307, 310, 311, 312, 315, 316, 317), measured anchor liveness, and rc before/after; the hygiene-move disposition this plan had originally named was REFUSED on every one of the eleven legs, so it appears in no card, fence or record - t108 corrects this line to the shipped pair
>   (309 KEEPS rc=1 for its stale BASE literal and says so); frozen neighbours - led by
>   t106's checker and findings record - byte-identical; delta pure against a
>   run-time-derived base and groom-reproducible.
>   Files: `docs/state/merge_test_index.json`,
>   `docs/state/outputs/t105_repremise_decisions.json`. Depends: [].
> - t106 - Requirement: existing checker/hygiene anchors from t104 only; no new REQ-ID.
>   Title: give `docs/tools/leg_path_pin_audit.py` a decoded-base64 view while the
>   plaintext view stays byte-stable, and ship the superset findings record.
>   Acceptance: against a run-time-derived pre-t105 index the upgrade reports all 11
>   hidden legs with `via=decoded_base64` and keeps both plaintext legs, with exit 0 on a
>   parseable index; every (leg, path, status) triple the shipped t104 auditor derived is
>   still derived, and `t104_hygiene_findings.json` is byte-frozen; a planted pin that
>   exists in NO location is named, classified `missing_everywhere` and counted (+1
>   `broken_pins`) with rc still 0, and `--expect-pins` stays the only opt-in nonzero
>   path; the new findings record is reproducible from a fresh run; the auditor is proven
>   read-only and index-neutral dynamically (hashes before/after three runs) and
>   statically (stdlib-only imports, no write-mode open/unlink/replace/subprocess); delta
>   pure - ZERO index bytes - and groom-reproducible.
>   Files: `docs/tools/leg_path_pin_audit.py`,
>   `docs/state/outputs/t106_checker_b64_findings.json`. Depends: [].

**Hard rules inherited by both cards.** Delta-purity fences DERIVE their base at run time
(`HEAD^` first, then `merge-base(main, HEAD)`, then `merge-base(origin/main, HEAD)`,
printing each candidate, its rejection reason and the acceptance); pinning BASE to a
main-tip-at-groom literal remains the t102 anti-pattern. `docs/log/orchestrator_wal.jsonl`
is EXCLUDED from both ALLOWED sets. `ac_hash` is authored at groom by the t58 recipe
(sha256 over the JSON-compact array of the six fenced bash bodies in ac1..ac6 order,
CR-stripped and trimmed); the groom handoffs' `verification_commands` are BYTE-IDENTICAL
to the card fences; and both cards were proved to BITE - each fence GREEN on a correct
product and RED on a plausible violation, measured in throwaway clones before landing
(t102/t103 precedent).

**Deliberate non-coverage.** Leg 230 (t62) and leg 279 (t78) are DISCLOSED non-repairs on
t105: 230 is the pre-existing frozen-RED analogue and 279's card is the documented live
exemption from t104 - both are asserted untouched. Leg 309's stale BASE literal
(`67c9db975d75`) is NOT repaired by this phase; it is recorded in the decision record so
the orchestrator owns it. `docs/state/outputs/t104_hygiene_findings.json` is NOT
regenerated - it is byte-frozen under t104 custody and is the reference t106's
byte-stability fence is measured against; t106 ships a NEW superset record instead and the
choice is stated in the card.
## phase_18_record_stamp_plan_drift - Findings-record index stamping, and the plan.md vocabulary cleanup (operator authorization, WAL 1248/1249)

**Scope ruling (operator, WAL 1249).** TWO SEPARATE CARDS, 比照前例 with phase_16/17
(operator wording 2026-10-22): the two follow-ups of phase_17's review (WAL 1248 items W1
and W3) are authorized as separate cards with DISJOINT surfaces, parallel-safe in
either merge order. Item 3 of WAL 1248 (the 193-of-318 legs missing the `ac` key) is
EXPLAINED and HELD in the standing backlog - NOT dispatched, not covered here.

**Measured base state this plan relies on (commands actually run at survey, HEAD
1128b97).**
- t106's shipped record `docs/state/outputs/t106_checker_b64_findings.json` is a frozen
  PRE-T105 snapshot. Replaying its own ac4 cross-check on merged main measures EXACTLY
  10 path-membership mismatches (legs 282, 306, 308, 309, 310, 311, 312, 315, 316, 317 -
  0-based array indices into the tests array, always with issue_id and ac per WAL
  1240 W2) and EXACTLY 10 classification drifts (record `moved` vs fresh `present`);
  the leg SET and the headline counts still agree (13 legs, pinned_legs=13,
  broken_pins=0, exit 0). Leg 230's two paths and leg 307's five paths already agree
  with today's tree, so they are not in the drift set.
- Index provenance measured: HEAD's index blob is
  `a4e6509856cf2029e0951facf07ac98eeb8d0265` (blob id of the CR-normalized bytes;
  sha256 of those bytes
  `5790c1f91f311d8c82c524e042fb6e6a1027994d68387ee2ed4afb6399dc8162`), introduced by
  commit `c6dc6f3f` (t105's re-premise). The index blob at `4dff135d` (blob id
  `03f01d4979141ae555ea47f5a1ec933595bf06fe`, sha256
  `72a01d395b1bc15415979f0dc274ab626c9322de026e5605c689095a38d43c02`) REPRODUCES the
  t106 record's per-leg observations exactly when the shipped checker is replayed
  against it in today's tree - measured at survey by walking the index's commit
  history. These values are provenance ONLY; every fence derives blobs at run time and
  embeds no literal commit or digest.
- t105's shipped decision record uses `guard_correct_semantics` for legs 306/307/310/
  311/312/315/316/317 and `read_closed` for legs 282/308/309 (0-based, with issue_id
  and ac per WAL 1240 W2). The phase_17 section above still carries a hygiene-move
  disposition word that never reached any card, fence or record, a rejection claim
  about the guard-semantics disposition for all eleven legs, and the skipped-probe
  guard mechanism sentence that t105 measured and REJECTED; t108 corrects all three.
  (Deliberate style rule for this whole section: the rejected strings are DESCRIBED,
  never quoted - a rejected string quoted anywhere in plan.md is exactly what the
  t108 global-absence fences RED on.)

**Numbering convention (WAL 1240 W2, binding on both cards).** All leg numbers are
0-BASED ARRAY INDICES into `merge_test_index.json`'s `tests` array, always written
WITH their `issue_id` and `ac`, never bare - the orchestrator sweep runner prints
1-based ordinals.

> - t107 - Requirement: existing checker/hygiene anchors from t104/t106 only; no new
>   REQ-ID.
>   Title: make findings-record replay index-state EXPLICIT - stamp the generating
>   index blob into the record format going forward, ship a stamped companion record
>   generated against the merged index, and give `docs/tools/leg_path_pin_audit.py` an
>   `--against-record` cross-check that reports EXPECTED vs DRIFT instead of raw
>   mismatch.
>   Acceptance: the new record carries an `index_stamp` whose values are MEASURED
>   against the worktree index at run time (git blob id, sha256 of the CR-normalized
>   bytes, byte length), never quoted; the historical records
>   (`t104_hygiene_findings.json`, `t106_checker_b64_findings.json`) are byte-identical
>   to their base blobs and the t106 record gained no stamp key; a run-time-derived
>   historical index blob (walked from `git log -- <index>`, no literal commit or
>   digest) REPRODUCES the t106 record's observations and differs from HEAD's index
>   blob - the drift is named, not hidden; `--against-record` classifies every replay
>   observation EXPECTED or DRIFT, exits 0 on a stamped no-drift replay, exits 1 (with
>   a printed gate line) on stamped same-blob drift, and reports UNSTAMPED with exit 0
>   for a pre-stamp record; the checker's detection stays byte-stable (same 13-leg pin
>   set, broken_pins=0, dirty_b64_legs=0) and read-only (hashlib the sole import
>   admission); delta pure against a run-time-derived base, ZERO index bytes, and the
>   sibling's `docs/plan.md` surface frozen.
>   Files: `docs/tools/leg_path_pin_audit.py`,
>   `docs/state/outputs/t107_record_stamp_findings.json`. Depends: [].
> - t108 - Requirement: none - documentation truth only; no new REQ-ID.
>   Title: plan.md phase_17 vocabulary cleanup - align the disposition vocabulary and
>   the mechanism prose with the shipped t105 records.
>   Acceptance: the hygiene-move disposition word and the all-eleven rejection claim
>   appear NOWHERE in `docs/plan.md` (global absence, so they cannot be reintroduced
>   by this section either); the corrected disposition line (the shipped 3-live/8-dead
>   split, leg lists derived from the shipped decision record) appears inside the
>   phase_17 section; the rejected skipped-probe mechanism sentence is gone (measured
>   on whitespace-normalized text) and the measured-liveness sentence remains; every
>   change lies inside the phase_17 section - the rest of plan.md is byte-identical to
>   its base blob; every historical handoff, findings record, the index, the checker
>   and the bookkeeping are byte-identical to their base blobs; delta pure against a
>   run-time-derived base and groom-reproducible.
>   Files: `docs/plan.md`. Depends: [].

**Hard rules inherited by both cards.** Delta-purity fences DERIVE their base at run
time (`HEAD^` first, then `merge-base(main, HEAD)`, then `merge-base(origin/main,
HEAD)`, printing each candidate, its rejection reason and the acceptance); pinning
BASE to a main-tip-at-groom literal remains the t102 anti-pattern.
`docs/log/orchestrator_wal.jsonl` is EXCLUDED from both ALLOWED sets. `ac_hash` is
authored at groom by the t58 recipe (sha256 over the JSON-compact array of the six
fenced bash bodies in ac1..ac6 order, CR-stripped and trimmed); the groom handoffs'
`verification_commands` are BYTE-IDENTICAL to the card fences; and both cards must
BITE - each fence GREEN on a correct product and RED on a plausible violation,
measured in throwaway clones before landing (t102/t103 precedent).

**Custody.** `docs/state/merge_test_index.json` carries ZERO bytes on both cards - no
index write is needed (the stamp is measured, not stored in the index), so the WAL
1248 W2 8-property index-amendment policy is NOT invoked; if any future card wants an
index or frozen-record write, that card must amend in writing and satisfy all eight
properties. `docs/state/outputs/t104_hygiene_findings.json` and
`t106_checker_b64_findings.json` stay byte-frozen (t104/t106 custody); t107 ships a
NEW stamped companion record instead. The phase_17 survey and review_plan handoffs
are historical records and are NOT rewritten - t108 fixes plan.md only.
