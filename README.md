# expense-tracker-dashboard

Expense Tracker Dashboard - a FastAPI + React dashboard for tracking
expenses and monthly budgets.

The stack is FastAPI on the API side and React on the front end. The
feature list is below, the seeded demo gets real data onto your own
machine with one command, and the reviewer evidence - verification
records and checklists - lives in `docs/verification.md`.

## Features

| Feature | Status | Evidence |
|---|---|---|
| Expense tracking (auth, categories, expenses, budgets, audit) | available | `docs/issues/closed/` |
| Dashboard (KPI cards, five charts, month switch, recent list) | available | `docs/criteria/dashboard_verification.md` |

Dashboard evidence is generated hermetically by
`backend/scripts/dashboard_verification.py`; the generated record lives in
`docs/criteria/dashboard_verification.md` (REQ-PLAN-041 cross-checks,
criteria-table rows 17-26/32, recorded REQ-PROD-020 timings), and the
verification method behind it is summarised in `docs/verification.md`.

- Reviewer screenshots: [docs/screenshots.md](docs/screenshots.md)

### API overview

The dashboard reads its numbers through six read-only endpoints under
`/api/v1/dashboard/`. Every one of them needs a bearer token in the
Authorization header; the request parameters and response shapes are
documented in [docs/api.md](docs/api.md) and machine-readable in
[openapi.yaml](openapi.yaml).

- `/api/v1/dashboard/summary?year_month=YYYY-MM`
- `/api/v1/dashboard/by-category?year_month=YYYY-MM`
- `/api/v1/dashboard/trend?months=N`
- `/api/v1/dashboard/cumulative?year_month=YYYY-MM`
- `/api/v1/dashboard/heatmap?weeks=N`
- `/api/v1/dashboard/recent?limit=N`

## Online demo

Try the app before building it. The seeded local demo path works today: one
command loads a fixed demo account and a deterministic recent expense
dataset into your own local database, and the dashboard renders from it
immediately.

```bash
npm run seed:demo
```

Then run the Quick Start commands below and sign in with the fixed account
demo@example.com / demo-password-123. The seed script touches only its own
demo rows and is safe to re-run.

A hosted demo address is a placeholder pending the published deployment, and
no URL is fabricated here: no public service has been published yet, so the
real address will be filled in when it exists. Until then, the seeded local
demo above is the demo path.

## Prerequisites

This is the whole host list. Install these three tools and nothing else:

- Node.js 20+ with npm (npm is the only daily command surface)
- uv (no Python to install - uv manages the interpreter inside
  backend/.venv)
- Git (to clone this repository)
- No Python knowledge is needed: uv installs and manages the interpreter,
  so you never install or configure Python yourself
- Docker is not needed and is not used locally
- No make or bash knowledge is needed: GNU make is not needed for the npm
  path, and the carried make targets stay documented under Alternative
  paths below for Linux/WSL users

That is the whole host list: there is nothing else to install.

## Quick Start

Eight numbered steps bring the whole app up locally, natively on Windows 11
from the repository root (cmd.exe or PowerShell - no make, no bash, no
Docker):

```bash
# 0. Clone the repository
git clone <repo-url> && cd expense-tracker-dashboard

# 1. Detect the environment state (host tools, dev ports, venv, frontend deps)
npm run check

# 2. Create the local environment file (placeholders only - fill secrets locally)
cp .env.example .env

# 3. Build whatever is missing (win32 backend venv, dev.db, frontend deps)
npm run setup:local

# 4. Run both servers: backend on http://localhost:8000 and frontend on http://localhost:5173
npm run dev

# 5. Open http://localhost:5173 in your browser

# 6. Register an account (first run only - a fresh database has no account yet)

# 7. Load the deterministic demo dataset for the fixed demo account
npm run seed:demo

# 8. Stop both servers again when you are done
npm run stop
```

Both servers log into one interleaved stream prefixed `[backend]` and
`[frontend]`, and dev prints the two clickable URLs when they are up. The
backend health contract is `GET /api/v1/health` (served directly at
`http://localhost:8000/api/v1/health` and proxied by the vite dev server
through `/api`). Configuration lives in `.env` (never committed);
`.env.example` lists every variable with placeholder values. See
`docs/requirements/Chapter3_TechStack.md` section 3.10 for the variable
reference.

The `npm run seed:demo` step is safe to re-run: the seed wipes and rebuilds
only the fixed demo account (`demo@example.com` / `demo-password-123`) and
its own demo rows, never your own accounts or data, and the dataset is
deterministic - the same demo rows every time. Sign in with that account to
see the populated dashboard. To stop both servers again, see the
`## Stopping the app` section below.

## Stopping the app

Two sanctioned ways to stop the dev servers:

- Ctrl+C in the `npm run dev` console. dev.ts registers SIGINT and SIGTERM
  handlers and tears both children down before it exits.
- `npm run stop` from any other console - the guaranteed reaper when the dev
  console is already gone or an earlier run left an orphan behind:

```bash
npm run stop
```

What the reaper does (the same behaviour `scripts/dev/stop.ts` implements):

- It is SCOPED to the two dev ports 8000 and 5173 only - no other port is
  ever touched.
- For every occupied dev port it kills the owning process tree and prints
  the PID it killed (`cleaned port 8000 - killed PID <pid>`).
- It is idempotent: on a clean tree it exits 0 and prints that both dev
  ports are already free (nothing to clean), so re-running it is always safe.
- After cleaning it prints how many orphan listeners it reaped and states
  that no other port was touched, so the operator can see the scope of what
  happened (`reaped N orphan listener(s) on the dev ports`).

## Troubleshooting

The four failure modes the dev scripts actually print, each with the
remedy the scripts themselves name:

| Symptom (what you see) | Why it happens | Remedy (what the scripts tell you to run) |
|---|---|---|
| check or dev reports an occupied dev port 8000 or 5173 with its owning PID | a previous run left an orphan listener; check reports occupied ports as reported only, not touched, and never kills them | run `npm run stop` (the port-scoped reaper), then `npm run dev` again |
| check reports `backend/.venv` missing (typical after a venv built under one platform is reused from the other) | the venv was never built for this platform, or it is unusable here | run `npm run setup:local`, which rebuilds `backend/.venv` with `uv sync --frozen` |
| check prints `host tool uv: MISSING (not on PATH)` | uv is not installed or not on PATH; check detects and reports host tools, it never installs them | install uv, then re-run `npm run check` and `npm run setup:local` |
| `http://127.0.0.1:5173` refuses the connection although dev printed the vite URL | vite binds the IPv6 loopback ::1, so the IPv4 literal never reaches it | open `http://localhost:5173/` instead of the 127.0.0.1 literal |

## Alternative paths - Linux/WSL via make

The GNU make surface below is the carried Linux/WSL alternative to the npm
Quick Start. The target table, the test commands and the lint commands with
their full rationale live in `docs/development.md`.

### Other targets

```bash
make setup
make migrate
```

### Running tests

```bash
make test
make test-backend
make test-frontend
```

### Linting

```bash
make lint
make lint-backend
make lint-frontend
```
## Local development modes

Two sanctioned local modes exist (REQ-CICD-025, REQ-CICD-026); pick one per
working session. Both read the same `.env` contract and target the same
migration surface (REQ-DB-082). The mode narrative and the compose,
migration and secret-rule rationale live in `docs/development.md`.

### Mode A - full Docker stack

```text
docker compose up --build
docker compose down
```

Builds the image and starts both compose services (`db` + `app`,
REQ-CICD-023); the container runs the migration in its start command
(REQ-DB-082, REQ-TECH-042).

### Mode B - hybrid (container database, host processes)

```text
docker compose up db
export DATABASE_URL=postgresql+psycopg://expense:change-me-locally@localhost:5432/expense_tracker
make migrate
make dev-backend
make dev-frontend
```

The database runs in the container and you run `make migrate` yourself
after pointing `DATABASE_URL` at it; the Vite dev server serves the SPA and
`uvicorn --reload` serves the API.

### Development versus production

Development uses the Vite dev server plus `uvicorn --reload`; production is
the single container built by the `Dockerfile` (REQ-CICD-025, REQ-CICD-026,
REQ-DB-082). Secrets never enter the build context (REQ-CICD-070).
## Repository layout

- `backend/` - FastAPI application (uv-managed Python 3.12 project)
- `frontend/` - React + TypeScript single-page app (Vite, npm)
- `docs/` - requirements, plan, commands, and coding standards
- `e2e/`, `ops/`, `security/` - placeholders for later phases

See `docs/commands.md` for the raw toolchain commands and
`docs/coding_standards.md` for contribution style.

## Documentation map

- [Verification evidence](docs/verification.md)
- [Development guide](docs/development.md)
- [Screenshots](docs/screenshots.md)

## Screenshots

The screenshot prose, the capture recipe and the seed shape moved to
`docs/screenshots.md`; the four reviewer-facing PNG files stay in
`screenshots/` (REQ-DOC-040, REQ-DOC-041, REQ-DOC-082).

| File |
|---|
| `screenshots/dashboard.png` |
| `screenshots/expense-form.png` |
| `screenshots/budget-page.png` |
| `screenshots/health-check.png` |
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE)
file for details.

## Deployment on Render

PLACEHOLDER - this deployment is pending and has not been published.
No Render service is live yet, no live address is fabricated here, and
the address stays unpublished until residual issue #61 is resolved: the
operator still needs to configure the `RENDER_DEPLOY_HOOK` secret and
import the blueprint. The procedure below is what runs once #61 lands.

### Why Render

Render hosts the single Docker web service and the managed PostgreSQL
instance on the free tier from one Blueprint file, so the review team can
deploy, review, and roll back without owning any infrastructure
(REQ-CICD-030, REQ-TECH-061).

### First deployment

1. Import the repository as a Render Blueprint - `render.yaml` is the
   deployment-as-code deliverable and is not imported or live yet.
2. Add the `RENDER_DEPLOY_HOOK` value as a GitHub secret so `deploy.yml`
   can trigger releases (the hook URL itself is never committed).
3. Render builds the Docker image, runs migrations at container start,
   and serves the app; verify `/api/v1/health` turns green
   (REQ-CICD-036).

### Free tier

The free PostgreSQL instance expires after 30 days and the free web
service sleeps when idle, so the first request after a quiet period pays
a cold start of tens of seconds (REQ-TECH-061, REQ-CICD-033,
REQ-CICD-040). Budget the review window accordingly: expect one cold
start per idle gap, keep the database plan within free limits, and treat
any longer outage as a redeploy question, not an incident (REQ-CICD-042).

### UptimeRobot

Once a service exists, ping `/api/v1/health` from UptimeRobot every
10 min to keep the free service warm and to get an outside-the-platform
view of availability (REQ-CICD-041). Reviewers should open the deployed
URL early in the session so the reported latency is a warm-service
number, not the cold start (REQ-CICD-043).