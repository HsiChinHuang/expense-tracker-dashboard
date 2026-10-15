# Development guide

This document is the relocation home for the internal reviewer and contributor
material that `README.md` carried until t66. It absorbed three README sections
and holds their full prose and rationale; the operator README keeps only the
compact command surface the carried gates read.

## Sections absorbed from README.md

| README section absorbed | What moved here |
|---|---|
| `Alternative paths - Linux/WSL via make` | The Linux/WSL make narrative, the full target table, and the test and lint rationale |
| `Local development modes` | The two-mode narrative and the compose, migration and secret-rule rationale behind it |
| `Dashboard API endpoints` | The endpoint table detail and its verification paragraph |

## Alternative paths - Linux/WSL via make

The GNU make surface is the carried Linux/WSL path. It is an alternative, not
the operator path: on Windows 11 use the npm commands in the README Quick
Start. Every make target listed here still works where make and bash exist.

### Other targets

| Target | Purpose |
|---|---|
| `make setup` / `make setup-backend` / `make setup-frontend` | Install dependencies |
| `make dev` | Hint: run backend and frontend in two terminals |
| `make down` | Stop services (services land in phase 5) |
| `make migrate` | Database migrations (Alembic, lands in phase 2) |
| `make seed` | Seed data (lands in phase 3) |
| `make e2e` | End-to-end tests (Playwright, lands in phase 5) |
| `make security` | Security scans (gitleaks/semgrep/trivy, land in phase 7) |

### Running tests

`make test` runs both suites (backend pytest plus frontend vitest);
`make test-backend` and `make test-frontend` run one stack each. The backend
suite runs in `backend/` via uv, the frontend suite runs in `frontend/` via
npm, so neither needs a host Python or a global toolchain.

### Linting

`make lint` runs both stacks (ruff plus mypy for the backend, eslint plus tsc
for the frontend); `make lint-backend` and `make lint-frontend` scope the run
to one stack. The type check is strict on purpose: mypy runs with strict
settings so a type regression fails the lint target rather than the review.

## Local development modes

Two sanctioned local modes exist; pick one per working session. Both read the
same `.env` contract and target the same migration surface.

### Mode A - full Docker stack

One command builds the multi-stage image and starts both compose services
(`db` + `app`):

```text
docker compose up --build
docker compose down
```

The app container runs `alembic upgrade head` in its start command before
uvicorn serves the API and the built frontend from `backend/static`. The API
is on `http://localhost:8000` with the health contract at `/api/v1/health`.

### Mode B - hybrid (container database, host processes)

Only the database is containerized; the API and SPA run as host processes
with hot reload:

```text
docker compose up db
export DATABASE_URL=postgresql+psycopg://expense:change-me-locally@localhost:5432/expense_tracker
make migrate
make dev-backend
make dev-frontend
```

`make migrate` is the manual migration step in this mode - the host process
has no container-start hook, so you run the migrations yourself after the
exported `DATABASE_URL` points at the containerized database. The Vite dev
server serves the SPA on `http://localhost:5173`, the API on `:8000`.

### Development versus production

Development uses the Vite dev server plus `uvicorn --reload` against a
managed or containerized PostgreSQL. Production is the single container
built by the `Dockerfile`: FastAPI serves the built frontend static files
with an SPA fallback, and the same `alembic upgrade head` migration runs in
the container start command. Secrets never enter the build context; the
compose placeholders are replaced by the platform at deploy time.

## Dashboard API endpoints

All six endpoints require a bearer token and are read-only. The frontend
never re-derives a displayed figure: every number on the dashboard comes
from one of these queries.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/dashboard/summary?year_month=YYYY-MM` | Seven-key monthly summary (total, budget, remaining, percentage, over-budget, category count) |
| GET | `/api/v1/dashboard/by-category?year_month=YYYY-MM` | Category breakdown, amount-descending |
| GET | `/api/v1/dashboard/trend?months=N` | Contiguous month trend (1..24, default 6), empty months included |
| GET | `/api/v1/dashboard/cumulative?year_month=YYYY-MM` | One cumulative point per calendar day |
| GET | `/api/v1/dashboard/heatmap?weeks=N` | Monday-aligned seven-day heatmap rows (1..52, default 12) |
| GET | `/api/v1/dashboard/recent?limit=N` | Newest expenses (1..50, default 10) |

The endpoint contract is verified hermetically by
`backend/scripts/dashboard_verification.py`, whose generated evidence lives
in `docs/criteria/dashboard_verification.md`.
