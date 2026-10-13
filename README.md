# expense-tracker-dashboard

Expense Tracker Dashboard — a FastAPI + React dashboard for tracking expenses,
built per `docs/requirements/` (see Chapter 3 for the tech stack and
Chapter 17 for the development plan). This repository is under active
development; phase 1 provides the project skeleton, health endpoint, and the
command surface documented below.

## Features

| Feature | Status | Evidence |
|---|---|---|
| Expense tracking (auth, categories, expenses, budgets, audit) | merged | `docs/issues/closed/` |
| Dashboard (KPI cards, five charts, month switch, recent list) | merged (phase 4) | `docs/criteria/dashboard_verification.md` |

The dashboard feature is verified hermetically by
`backend/scripts/dashboard_verification.py`, whose generated evidence lives in
`docs/criteria/dashboard_verification.md` (REQ-PLAN-041 cross-checks,
criteria-table rows 17-26/32, recorded REQ-PROD-020 timings).

### Dashboard API endpoints

All six endpoints require a bearer token and are read-only:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/dashboard/summary?year_month=YYYY-MM` | Seven-key monthly summary (total, budget, remaining, percentage, over-budget, category count) |
| GET | `/api/v1/dashboard/by-category?year_month=YYYY-MM` | Category breakdown, amount-descending |
| GET | `/api/v1/dashboard/trend?months=N` | Contiguous month trend (1..24, default 6), empty months included |
| GET | `/api/v1/dashboard/cumulative?year_month=YYYY-MM` | One cumulative point per calendar day |
| GET | `/api/v1/dashboard/heatmap?weeks=N` | Monday-aligned seven-day heatmap rows (1..52, default 12) |
| GET | `/api/v1/dashboard/recent?limit=N` | Newest expenses (1..50, default 10) |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (provides `uv`; typically installed to `~/.local/bin`)
- Node.js 20+ with npm (on WSL hosts the npm/node Windows binaries are used
  through `cmd.exe`; the Makefile detects this automatically)
- Python 3.12 (managed by `uv sync` for the backend)
- GNU make and bash
- Git

## Quick Start

From a clean checkout, run the following from the repository root:

```bash
# 1. Clone the repository
git clone <repo-url> && cd expense-tracker-dashboard

# 2. Create the local environment file (placeholders only — fill in secrets locally)
cp .env.example .env

# 3. Install both stacks (backend via uv, frontend via npm)
make setup

# 4. Run the backend API (http://localhost:8000, health check at /api/v1/health)
make dev-backend

# 5. Run the frontend dev server (http://localhost:5173) — in a second terminal
make dev-frontend
```

Configuration lives in `.env` (never committed); `.env.example` lists every
variable with placeholder values. See
`docs/requirements/Chapter3_TechStack.md` §3.10 for the variable reference.

## Local development modes

Two sanctioned local modes exist (REQ-CICD-025, REQ-CICD-026); pick one per
working session. Both read the same `.env` contract and target the same
migration surface (REQ-DB-082).

### Mode A - full Docker stack

One command builds the multi-stage image and starts both compose services
(`db` + `app`, REQ-CICD-023):

```text
docker compose up --build
docker compose down
```

The app container runs `alembic upgrade head` in its start command before
uvicorn serves the API and the built frontend from `backend/static`
(REQ-DB-082, REQ-TECH-042). The API is on `http://localhost:8000` with the
health contract at `/api/v1/health`.

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

`make migrate` is the manual REQ-DB-082 step in this mode — the host process
has no container-start hook, so you run the migrations yourself after the
exported `DATABASE_URL` points at the containerized database. The Vite dev
server serves the SPA on `http://localhost:5173`, the API on `:8000`.

### Development versus production

Development uses the Vite dev server plus `uvicorn --reload` against a
managed or containerized PostgreSQL. Production is the single container
built by the `Dockerfile`: FastAPI serves the built frontend static files
with an SPA fallback, and the same `alembic upgrade head` migration runs in
the container start command (REQ-CICD-025, REQ-CICD-026, REQ-DB-082). Secrets
never enter the build context (REQ-CICD-070); the compose placeholders are
replaced by the platform at deploy time.

## Running tests

```bash
# Both suites (backend pytest + frontend vitest)
make test

# Backend only (pytest, runs in backend/ via uv)
make test-backend

# Frontend only (vitest, runs in frontend/ via npm)
make test-frontend
```

## Linting

```bash
# Both stacks (ruff + mypy for backend, eslint + tsc for frontend)
make lint

make lint-backend
make lint-frontend
```

## Other targets

| Target | Purpose |
|---|---|
| `make setup` / `make setup-backend` / `make setup-frontend` | Install dependencies |
| `make dev` | Hint: run backend and frontend in two terminals |
| `make down` | Stop services (services land in phase 5) |
| `make migrate` | Database migrations (Alembic, lands in phase 2) |
| `make seed` | Seed data (lands in phase 3) |
| `make e2e` | End-to-end tests (Playwright, lands in phase 5) |
| `make security` | Security scans (gitleaks/semgrep/trivy, land in phase 7) |

## Repository layout

- `backend/` — FastAPI application (uv-managed Python 3.12 project)
- `frontend/` — React + TypeScript single-page app (Vite, npm)
- `docs/` — requirements, plan, commands, and coding standards
- `e2e/`, `ops/`, `security/` — placeholders for later phases

See `docs/commands.md` for the raw toolchain commands and
`docs/coding_standards.md` for contribution style.

## Screenshots

Four reviewer-facing images captured from one measured local run of the
merged stack (uvicorn on 127.0.0.1:8000 with the SQLite fallback engaged, the
Vite dev server on 127.0.0.1:5173, Playwright Chromium at a 1440x900 viewport,
no Docker daemon anywhere). Every figure in every image is fictional demo data
seeded through the public API - no real personal data appears in any image
(REQ-DOC-040, REQ-DOC-041, REQ-DOC-082).

| File | What it shows |
|---|---|
| `screenshots/dashboard.png` | The four KPI cards, the five charts, the budget progress bar and the recent list for a seeded month |
| `screenshots/expense-form.png` | The Add expense form on the expenses page, filled with one demo entry |
| `screenshots/budget-page.png` | The budget page: the month budget, the progress surface and the set-month history |
| `screenshots/health-check.png` | The `/api/v1/health` payload as served through the dev-server proxy |

Each file is a PNG under 500 KB. The capture recipe and the exact seed shape
are pinned in the t52 grooming card under `docs/issues/`; the images are
evidence artifacts, not test fixtures, and no gate hashes their pixels (the
phase_8 ruling is that screenshots are measured artifacts gated on presence,
magic bytes, viewport width and size).

## Criteria mapping

One row per Chapter 24.3 quality-acceptance table (rows 1-15) - the
reviewer's map from each check to the requirement and the file that holds
its evidence (REQ-DOC-081, REQ-PROJ-005).

| # | Check (Chapter 24.3) | Requirement | Evidence to open |
|---|---|---|---|
| 1 | README under 500 lines | REQ-DOC-010 | `wc -l README.md` (this file) |
| 2 | All docs present | REQ-DOC-002 | `docs/` (see Evidence checklist below) |
| 3 | Screenshots present | REQ-DOC-040 | `screenshots/dashboard.png`, `screenshots/expense-form.png`, `screenshots/budget-page.png`, `screenshots/health-check.png` |
| 4 | Criteria mapping present | REQ-PROJ-005, REQ-DOC-081 | this section |
| 5 | AI workflow documented with real sessions | REQ-AI-110 to REQ-AI-113 | `docs/ai-workflow.md` (lands with t50) |
| 6 | Correction log present | REQ-AI-120 to REQ-AI-122 | `docs/ai-workflow.md` (lands with t50) |
| 7 | Agent Extension Pack functional | REQ-EXT-001 to REQ-EXT-083 | `docs/agent-extension-pack.md` |
| 8 | Hook tests pass | REQ-EXT-072 | `docs/criteria/agent_pack_verification.md` |
| 9 | Permissions documented | REQ-EXT-060 | `docs/permissions.md` |
| 10 | Security artifacts present | REQ-SEC-001 | `security/` (8 artifacts) |
| 11 | Ops artifacts present | REQ-OPS-002 | `ops/` (5 artifacts) |
| 12 | Diagnosis reproducible | REQ-OPS-042 | `ops/diagnosis.md` |
| 13 | Deployment record present | REQ-OPS-060 | `ops/deployment-health.md` |
| 14 | Peer reviewer can reproduce in < 10 min | REQ-PROJ-009, REQ-DOC-071 | Local verification in five minutes below |
| 15 | README 5-minute verification path | REQ-DOC-070 | both five-minute sections below |

## Evidence checklist

One row per Chapter 24.5 final-project criteria table (criteria 1-14) -
the REQ-DOC-072 checklist mapping each of the 14 criteria to the specific
file (or directory) a reviewer opens.

| # | Criterion (Chapter 24.5) | Requirement range | File to open |
|---|---|---|---|
| 1 | Problem Description | REQ-PROJ-001 to REQ-PROD-007 | `product-spec.md` |
| 2 | AI Workflow | REQ-AI-001 to REQ-AI-143 | `docs/ai-workflow.md` (lands with t50) |
| 3 | Architecture | REQ-TECH-001 to REQ-ARCH-082 | `docs/architecture.md` (lands with t51) |
| 4 | Frontend | REQ-FE-001 to REQ-FE-144 | `frontend/` |
| 5 | API Contract | REQ-API-001 to REQ-API-114 | `openapi.yaml` |
| 6 | Backend | REQ-BE-001 to REQ-BE-152 | `backend/` |
| 7 | Database | REQ-DB-001 to REQ-DB-135 | `backend/alembic/` |
| 8 | Containerization | REQ-CICD-020 to REQ-CICD-026 | `Dockerfile`, `docker-compose.yml` |
| 9 | Integration Testing | REQ-TEST-020 to REQ-TEST-045 | `e2e/`, `backend/tests/integration/` |
| 10 | Deployment | REQ-CICD-030 to REQ-CICD-062 | `render.yaml`, `ops/deployment-health.md` |
| 11 | CI/CD | REQ-CICD-010 to REQ-CICD-083 | `.github/workflows/` |
| 12 | Agent Extension Pack | REQ-EXT-001 to REQ-EXT-083 | `docs/agent-extension-pack.md` |
| 13 | Security/Audit/DevOps | REQ-SEC-001 to REQ-OPS-113 | `security/`, `ops/` |
| 14 | Reproducibility | REQ-PROJ-009, REQ-DOC-070 to REQ-DOC-072 | this README, `Makefile` |

## Live verification in five minutes

Reviewer procedure against the deployed URL (REQ-DOC-070). Status, stated
honestly: the public Render URL is DEFERRED for live attestation - this
environment has no egress and the stored register records RENDER_DEPLOY,
UPTIMEROBOT_MONITOR and LIVE_COLD_START as deferred (egress_forbidden),
so this README documents the procedure without claiming the deployment
was verified live in CI. Open the deployed URL early: the free tier pays
a cold start after each idle gap (see Free tier above).

1. Open the live URL (the Render service named in `render.yaml`).
2. Register an account (or log in).
3. Add an expense.
4. Set a budget for the month.
5. Verify the five charts (trend, cumulative, by-category pie, weekly
   heatmap, and the KPI/recent surface) render from their own queries.
6. Switch month - every month-driven chart refetches.
7. Log out.

## Local verification in five minutes

The same seven steps with zero accounts (REQ-DOC-071, REQ-PROJ-009):

```bash
git clone <repo-url> && cd expense-tracker-dashboard
cp .env.example .env
docker compose up --build
```

1. Open http://localhost:8000 (the SPA plus the API in one container).
2. Register an account.
3. Add an expense.
4. Set a budget for the month.
5. Verify the five charts.
6. Switch month.
7. Log out, then `docker compose down`.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE)
file for details.

## Deployment on Render

The pipeline in `.github/workflows/` ships this app to Render after a green
E2E run; `render.yaml` is the Render Blueprint that declares the whole
deployment as code (REQ-CICD-030, REQ-CICD-036).

### Why Render

Render hosts the single Docker web service and the managed PostgreSQL
instance on the free tier from one Blueprint file, so the review team can
deploy, review, and roll back without owning any infrastructure
(REQ-CICD-030, REQ-TECH-061).

### First deployment

1. Push the branch and import the repository as a Render Blueprint.
2. Add the `RENDER_DEPLOY_HOOK` value as a GitHub secret so `deploy.yml`
   can trigger releases (the hook URL itself is never committed).
3. Render builds the Docker image, runs migrations at container start, and
   serves the app; verify `/api/v1/health` turns green (REQ-CICD-036).

### Free tier

The free PostgreSQL instance expires after 30 days and the free web service
sleeps when idle, so the first request after a quiet period pays a cold start
of tens of seconds (REQ-TECH-061, REQ-CICD-033, REQ-CICD-040). Budget the
review window accordingly: expect one cold start per idle gap, keep the
database plan within free limits, and treat any longer outage as a redeploy
question, not an incident (REQ-CICD-042).

### UptimeRobot

Ping `/api/v1/health` from UptimeRobot every 10 min to keep the free service
warm and to get an outside-the-platform view of availability (REQ-CICD-041).
Reviewers should open the deployed URL early in the session so the reported
latency is a warm-service number, not the cold start (REQ-CICD-043).
