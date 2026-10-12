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
