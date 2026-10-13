# Testing Guidelines

How tests are written, named, run, and reported in the Expense Tracker
Dashboard. The rules below restate `docs/coding_standards.md` and match
the real `Makefile` vocabulary on `main`; when the Makefile changes,
this page changes with it. Related:
[architecture.md](architecture.md), [api.md](api.md),
[design-system.md](design-system.md).

## Test layers

Four layers, each with its own runner and home:

1. **Backend unit** - pure logic (services, schemas, JWT, config) under
   `backend/tests/unit`, run by pytest with no database or network.
2. **Backend integration** - API routes and database behavior under
   `backend/tests/integration`, including per-migration tests and the
   SQLite fallback probe.
3. **Frontend unit/component** - Vitest + React Testing Library + MSW
   colocated `*.test.tsx` / `*.test.ts` files under `frontend/src`; MSW
   intercepts every network call so no backend is needed.
4. **E2E** - Playwright specs under `e2e/tests` driving the real stack
   (login, expense flow, month switching, user isolation).

## Backend rules

- Run everything through the Makefile: `make test-backend` runs the
  whole pytest suite; the CI splits use `make test-backend-unit` and
  `make test-backend-integration`; coverage runs use
  `make test-backend-cov`.
- Money paths assert on `Decimal` values and the 2-decimal string
  wire format - never on binary floats (the same discipline the
  services and `backend/app/schemas/expense.py` enforce).
- Database tests create their own data through the service layer or
  fixtures; they never mutate shared state across tests, and
  per-migration tests keep the Alembic head (currently `005`) covered.
- The SQLite fallback tests must not depend on a running PostgreSQL;
  the fallback latch is startup-only, so each test builds its own
  engine.

## Frontend rules

- Run through the Makefile: `make test-frontend` for the suite,
  `make test-frontend-cov` for the coverage run.
- Every test uses MSW handlers for network behavior; tests never hit a
  live API and never stub `fetch` by hand.
- Component tests query by role/label/text (accessibility-first
  queries), not by internal CSS structure.
- Charts and money rendering assert the API string is displayed
  verbatim - no re-formatting happens in components, and tests pin that.

## E2E rules

- `make e2e` installs the pinned Playwright dependency and runs the
  suite with the HTML report.
- Specs cover core flows only (register/login, expense CRUD, month
  switching, isolation between users); they do not re-test unit-level
  logic.
- E2E runs against the composed stack with a real database; on hosts
  where the stack cannot run, the suite is skipped with a recorded
  reason, never silently deleted.

## Coverage policy

Per REQ-TEST-003, coverage is **reported, not enforced** - no build
fails on a coverage number. The targets behind the report runs
(`make test-backend-cov` and `make test-frontend-cov`):

- backend unit: 80 percent and above (target 80)
- backend integration: 70 percent and above (target 70)
- frontend unit: 80 percent and above
- frontend components: 70 percent and above

A downward trend is reviewed like a failing test, but the gates stay
report-only by design.

## Naming conventions

From `docs/coding_standards.md`, verbatim:

- Test file name: `test_<module>.py` for backend files (for example
  `test_budget_service.py`).
- Test function name: `test_<action>_<expected>` (for example
  `test_login_wrong_password_returns_401`).
- Frontend colocated tests mirror the component file with a `.test.tsx`
  suffix; a new component ships with its own test file.

Every new test carries at least one meaningful assertion about behavior
- `assert True` style placeholders are rejected in review.

## What not to test

- Third-party library internals (Recharts rendering, FastAPI routing,
  SQLAlchemy ORM behavior) - test our usage, not their code.
- Private helper functions that have no observable behavior of their
  own; test them through their public caller.
- Migration history replay beyond the current head and the fallback
  path; already-landed migrations are frozen.
- Coverage thresholds themselves (they are reported, not enforced).
- Vendor output in `node_modules`, build artifacts, and generated
  files - they are not sources of truth and are excluded from every
  runner.

## Requirement-anchored test map

The matrix measured twenty-two testing ids with no citation. They are
recorded here in the document's own terms, mapped to the files that
actually carry the assertions. Where a requirement names a test file
that was shipped under the merged snake_case naming convention, the
table records the mapping instead of inventing a file: the requirement
texts name `format.test.ts`, `BudgetProgress.test.tsx`,
`WeeklyHeatmap.test.tsx`, `CategoryPieChart.test.tsx`,
`ExpenseForm.test.tsx` and `LoginPage.test.tsx`; the merged repo
carries the same coverage under `chart_data`-level util tests and the
snake_case component files listed below. Naming a requirement is not
evidence - the "asserts" column is.

| requirement | what it demands | where the assertion lives |
|---|---|---|
| REQ-TEST-001 | four test layers: backend unit (pytest), backend integration (pytest + TestClient/httpx), frontend unit/component (Vitest + RTL + MSW), E2E (Playwright) | the four runners in the Test layers section above |
| REQ-TEST-002 | assert behavior not implementation; one concept per test; independent; deterministic; fast by default | review rule; every colocated file follows it |
| REQ-TEST-010 | backend tests live in `backend/tests/` with `unit/` and `integration/` | `backend/tests/unit/`, `backend/tests/integration/` |
| REQ-TEST-021 | expenses API: create, negative/zero amount, three decimals, auth required, pagination | `backend/tests/integration/test_expense_api.py` (the requirement's name is `test_expenses_api.py`) |
| REQ-TEST-022 | budgets API: set, get nonexistent returns 0, invalid `year_month`, delete, delete-user cascade | `backend/tests/integration/test_budget_api.py` (requirement name `test_budgets_api.py`) |
| REQ-TEST-031 | money/percent formatting: integer, decimal, thousands, zero, negative | util assertions travel with `frontend/src/utils/chart_data.ts` and its consumers (`monthly_trend_chart.test.tsx` imports `formatMonthLabel` directly); requirement name `format.test.ts` |
| REQ-TEST-034 | budget bar green under 80%, yellow 80-100%, red over, capped at 100%, no-budget state | `frontend/src/components/common/budget_progress.test.tsx` (requirement name `BudgetProgress.test.tsx`) |
| REQ-TEST-035 | heatmap: 7 cells, zero is grey, max-zero window, skeleton while loading | `frontend/src/components/charts/weekly_heatmap.test.tsx` (requirement name `WeeklyHeatmap.test.tsx`) |
| REQ-TEST-036 | pie: empty state, renders with data, merges to Other beyond 6 categories | `frontend/src/components/charts/category_pie_chart.test.tsx` (requirement name `CategoryPieChart.test.tsx`) |
| REQ-TEST-037 | expense form: empty amount, negative, three decimals, cancel callback | `frontend/src/components/forms/expense_form.test.tsx` (requirement name `ExpenseForm.test.tsx`) |
| REQ-TEST-038 | login page: fields render, invalid email, invalid credentials | `frontend/src/pages/login_page.test.tsx` (requirement name `LoginPage.test.tsx`) |
| REQ-TEST-060 | backend data: in-memory/temp SQLite, seeded system categories, per-test users | `backend/tests/unit/test_dashboard_service.py`, `backend/tests/integration/test_database.py` build temp SQLite engines; category seeding runs through the app path |
| REQ-TEST-061 | frontend data: pure functions for unit tests, MSW handlers with fixed data for components, varied variants for pages | `frontend/src/test/handlers.ts` + `server.ts`, one server per process, per-test handler overrides |
| REQ-TEST-062 | E2E data: real backend and database, unique user per test | `e2e/fixtures/users.ts` `uniqueUser()`, used by every spec |
| REQ-TEST-080 | framework choices: pytest, pytest + TestClient, SQLite in-memory, Vitest, RTL, MSW, Playwright | the runners pinned in `Makefile`, `frontend/package.json`, `e2e/package.json` |
| REQ-TEST-081 | execution choices: coverage reported not enforced, CI runs unit + integration, E2E only on main, per-test fixtures, `Decimal` comparisons | the Coverage policy above + `.github/workflows/ci.yml` and `e2e.yml` |
| REQ-TEST-082 | error tests assert both status code and error code | e.g. `backend/tests/integration/test_expense_api.py` asserts `body["code"] == "INVALID_AMOUNT"` alongside `status_code == 422` - status code and error code are both pinned in every error path |
| REQ-FE-130 | frontend tests live beside source with `.test.ts(x)` suffixes across utils, charts, forms, pages | the colocated inventory under `frontend/src` |
| REQ-FE-131 | coverage targets: utils 90%+, charts 80%+, forms 80%+, pages 60%+, API modules mocked not tested directly | the report-only targets in the Coverage policy above |
| REQ-FE-132 | named example tests exist for the util, budget bar, heatmap, pie, form, and login surfaces | the six rows above (REQ-TEST-031/034-038) |
| REQ-STRUCT-072 | frontend tests colocated, backend tests separated in `tests/unit` + `tests/integration` | the layout both trees actually use |
| REQ-API-101 | integration tests assert response shapes match the OpenAPI schemas | `backend/tests/integration/test_expense_api.py` reads `client.get("/openapi.json")` and pins the operation set; the `{"detail", "code", "field"}` envelope constant is asserted key-by-key on every error body |

The mapping table is the honest version of the coverage claim: the
behavior each requirement demands is executed in the file named in the
third column, and where the requirement's file name differs from the
shipped file name, the difference is recorded rather than hidden.

When a new requirement lands with a behavior claim, the row above is
where its test gets registered: a requirement that no test file
executes is a gap, and the matrix reports it as one.
