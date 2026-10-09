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

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE)
file for details.
