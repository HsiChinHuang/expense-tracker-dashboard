# Chapter 14: CI/CD and Deployment

## 14.1 Overview

This chapter covers continuous integration, continuous deployment,
containerization, and the production deployment on Render. It maps to
Final Project Criteria 8, 10, and 11.

### 14.1.1 Criterion Mapping

| Criterion | Requirement | Where |
|---|---|---|
| 8. Containerization | Docker or Compose runs the full system | Dockerfile, docker-compose.yml |
| 10. Deployment | Working URL or clear proof | Render URL, ops/deployment-health.md |
| 11. CI/CD | Tests run automatically; deploy on pass | .github/workflows/ |

### 14.1.2 Pipeline Overview

```
Developer pushes to feature branch
        │
        ▼
┌───────────────────┐
│   Pull Request    │
│                   │
│  ci.yml runs:     │
│  - Backend tests  │
│  - Frontend tests │
│  - Integration    │
└─────────┬─────────┘
          │
          │ PR approved and merged
          ▼
┌───────────────────┐
│   Push to main    │
│                   │
│  e2e.yml runs:    │
│  - Docker Compose │
│  - Playwright E2E │
└─────────┬─────────┘
          │
          │ E2E passes
          ▼
┌───────────────────┐
│  deploy.yml runs: │
│  - Trigger Render │
│  - Verify health  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   Production      │
│   (Render)        │
└───────────────────┘
```

## 14.2 GitHub Actions Workflows

### 14.2.1 Directory Layout

```
.github/
└── workflows/
    ├── ci.yml
    ├── e2e.yml
    └── deploy.yml
```

### 14.2.2 ci.yml

Runs on every pull request and every push to main. Runs backend and
frontend tests in parallel, then integration tests.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  backend-test:
    name: Backend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: cd backend && uv sync --frozen

      - name: Lint
        run: cd backend && uv run ruff check .

      - name: Type check
        run: cd backend && uv run mypy app

      - name: Run unit tests
        run: cd backend && uv run pytest tests/unit -v

      - name: Run integration tests
        run: cd backend && uv run pytest tests/integration -v

      - name: Coverage
        run: cd backend && uv run pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: backend/coverage.xml

  frontend-test:
    name: Frontend Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Lint
        run: cd frontend && npm run lint

      - name: Type check
        run: cd frontend && npm run typecheck

      - name: Run tests
        run: cd frontend && npm run test -- --run

      - name: Coverage
        run: cd frontend && npm run test -- --run --coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: frontend-coverage
          path: frontend/coverage/

  compose-build:
    name: Docker Compose Build
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test]
    steps:
      - uses: actions/checkout@v4

      - name: Build and start stack
        run: docker compose up -d --build

      - name: Wait for health
        run: |
          for i in {1..30}; do
            if curl -sf http://localhost:8000/api/v1/health; then
              echo "Healthy"
              exit 0
            fi
            sleep 2
          done
          echo "Health check failed"
          docker compose logs
          exit 1

      - name: Stop stack
        if: always()
        run: docker compose down
```

### 14.2.3 e2e.yml

Runs on push to main only. Builds the full stack with Docker Compose
and runs Playwright E2E tests.

```yaml
name: E2E

on:
  push:
    branches: [main]

concurrency:
  group: e2e-${{ github.ref }}
  cancel-in-progress: true

jobs:
  e2e:
    name: End-to-End Tests
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: e2e/package-lock.json

      - name: Build and start stack
        run: docker compose up -d --build

      - name: Wait for health
        run: |
          for i in {1..60}; do
            if curl -sf http://localhost:8000/api/v1/health; then
              echo "Healthy"
              exit 0
            fi
            sleep 2
          done
          echo "Health check failed"
          docker compose logs
          exit 1

      - name: Install E2E dependencies
        run: cd e2e && npm ci

      - name: Install Playwright browsers
        run: cd e2e && npx playwright install --with-deps chromium

      - name: Run E2E tests
        run: cd e2e && npx playwright test
        env:
          E2E_BASE_URL: http://localhost:8000

      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: e2e/playwright-report/

      - name: Stop stack
        if: always()
        run: docker compose down -v
```

### 14.2.4 deploy.yml

Runs after e2e.yml succeeds. Triggers a Render deploy and verifies
the health endpoint.

```yaml
name: Deploy

on:
  workflow_run:
    workflows: [E2E]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    name: Deploy to Render
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    steps:
      - uses: actions/checkout@v4

      - name: Trigger Render deploy
        run: |
          curl -fsS -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"

      - name: Wait for Render to start
        run: sleep 60

      - name: Verify health
        run: |
          for i in {1..20}; do
            RESPONSE=$(curl -sf \
              https://expense-tracker-dashboard.onrender.com/api/v1/health \
              || echo "FAILED")
            if [[ "$RESPONSE" == *'"status"'* ]]; then
              echo "Health check passed:"
              echo "$RESPONSE"
              exit 0
            fi
            echo "Attempt $i failed, retrying..."
            sleep 15
          done
          echo "Health check failed after deployment"
          exit 1

      - name: Report deployment
        if: success()
        run: |
          echo "Deployed successfully"
          echo "URL: https://expense-tracker-dashboard.onrender.com"
```

### 14.2.5 Workflow Triggers Summary

| Workflow | Trigger | Runtime | Blocks Deploy |
|---|---|---|---|
| ci.yml | PR, push to main | ~5 min | Yes (PR must pass) |
| e2e.yml | Push to main | ~8 min | Yes (deploy waits) |
| deploy.yml | e2e.yml success | ~2 min | - |

### 14.2.6 Why No E2E on PR

| Reason | Explanation |
|---|---|
| Time | E2E takes 8+ minutes; PRs need fast feedback |
| Cost | GitHub Actions minutes are limited |
| Confidence | CI unit + integration tests catch most issues |
| Risk | E2E runs on main before deploy, so bugs are caught |

### 14.2.7 Concurrency

Both `ci.yml` and `e2e.yml` use `concurrency` to cancel in-progress
runs when a new push arrives. This saves CI minutes.

### 14.2.8 Caching

| Cache | Key | Purpose |
|---|---|---|
| uv | `backend/uv.lock` | Python dependencies |
| npm (frontend) | `frontend/package-lock.json` | Frontend dependencies |
| npm (e2e) | `e2e/package-lock.json` | E2E dependencies |
| Playwright | Playwright version | Browser binaries |

## 14.3 Containerization

### 14.3.1 Dockerfile

The application uses a two-stage build: Node builds the frontend, then
Python serves the built static files plus the API.

```dockerfile
# Stage 1: Build the frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Backend runtime
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install backend dependencies
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy backend code
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./

# Copy built frontend
COPY --from=frontend-builder /frontend/dist ./static

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 14.3.2 Dockerfile Design Decisions

| Decision | Rationale |
|---|---|
| Multi-stage build | Final image does not include Node or frontend dev dependencies |
| Alpine for Node | Smaller image for the build stage |
| Slim for Python | Smaller than full Python image, includes needed libs |
| uv for Python deps | Fast, matches local development |
| Non-root user | Security best practice |
| Static files copied | FastAPI serves them, single container |
| No dev dependencies | `--no-dev` keeps image small |
| Pinned versions | `node:20-alpine`, `python:3.12-slim` |

### 14.3.3 docker-compose.yml

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: expense
      POSTGRES_PASSWORD: expense
      POSTGRES_DB: expense
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U expense"]
      interval: 5s
      timeout: 3s
      retries: 10

  app:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://expense:expense@db:5432/expense
      JWT_SECRET: dev-secret-change-in-production
      CORS_ORIGINS: '["http://localhost:5173","http://localhost:8000"]'
      ENVIRONMENT: development
      APP_VERSION: 1.0.0
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

### 14.3.4 Compose Design Decisions

| Decision | Rationale |
|---|---|
| Two services | App and database |
| PostgreSQL 16 | Matches production |
| Health check on db | App waits for db to be ready |
| Health check on app | Compose can report health |
| Named volume | Data survives `docker compose down` |
| Single app container | Backend serves frontend |
| Explicit CORS | Allows local frontend dev if needed |

### 14.3.5 Development vs Production

| Aspect | Development | Production |
|---|---|---|
| Frontend | Vite dev server (:5173) | Static files served by FastAPI |
| Backend | uvicorn --reload (:8000) | uvicorn (:8000) |
| Database | PostgreSQL in Compose | Render PostgreSQL |
| Containers | 2 (app + db) | 1 (app) + managed db |
| Build | On every change | Once per deploy |

### 14.3.6 Local Development Modes

**Mode A: Full Docker**

```bash
docker compose up --build
```

Open http://localhost:8000

**Mode B: Hybrid (recommended for development)**

```bash
# Terminal 1: database
docker compose up db

# Terminal 2: backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 3: frontend
cd frontend && npm run dev
```

Open http://localhost:5173

Mode B is faster for development because Vite provides hot module
replacement and uvicorn reloads on backend changes.

## 14.4 Render Deployment

### 14.4.1 Why Render

| Reason | Explanation |
|---|---|
| No credit card | Free tier does not require payment info |
| Free PostgreSQL | 1 GB, 30-day expiry |
| Docker support | Deploys the existing Dockerfile |
| Health checks | Built-in support |
| GitHub integration | Automatic deploys |
| Free SSL | HTTPS on the default domain |

### 14.4.2 render.yaml

Infrastructure as code for the Render deployment.

```yaml
services:
  - type: web
    name: expense-tracker-dashboard
    runtime: docker
    plan: free
    region: oregon
    healthCheckPath: /api/v1/health
    autoDeploy: false
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: expense-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true
      - key: JWT_ALGORITHM
        value: HS256
      - key: JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        value: "1440"
      - key: JWT_ISSUER
        value: expense-tracker
      - key: JWT_AUDIENCE
        value: expense-tracker-api
      - key: CORS_ORIGINS
        value: '["https://expense-tracker-dashboard.onrender.com"]'
      - key: ENVIRONMENT
        value: production
      - key: APP_VERSION
        value: "1.0.0"

databases:
  - name: expense-db
    plan: free
    region: oregon
    databaseName: expense
    user: expense
```

### 14.4.3 Environment Variables

| Variable | Source | Notes |
|---|---|---|
| DATABASE_URL | Render database | Injected automatically |
| JWT_SECRET | Render generated | Random on first deploy |
| JWT_ALGORITHM | Static | HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Static | 1440 (24 hours) |
| JWT_ISSUER | Static | expense-tracker |
| JWT_AUDIENCE | Static | expense-tracker-api |
| CORS_ORIGINS | Static | Render URL |
| ENVIRONMENT | Static | production |
| APP_VERSION | Static | 1.0.0 |

### 14.4.4 Render Free Tier Limits

| Limit | Value | Impact |
|---|---|---|
| Web service RAM | 512 MB | Sufficient for demo |
| Web service CPU | 0.1 | Limited concurrency |
| Idle sleep | After 15 min | Cold start on next request |
| Monthly hours | 750 | Enough for one service |
| PostgreSQL storage | 1 GB | Enough for demo |
| PostgreSQL expiry | 30 days | Data lost; fallback handles it |
| Bandwidth | 5 GB/month | Enough for demo |
| Build minutes | 500/month | Enough for ~100 deploys |
| Custom domains | 2 | Not used in MVP |
| SSH access | Not available | Use Render logs |

### 14.4.5 Deployment Flow

```
1. Push to main
2. ci.yml runs tests
3. e2e.yml runs Playwright
4. deploy.yml triggers Render deploy hook
5. Render builds the Docker image
6. Render runs migrations (alembic upgrade head)
7. Render starts the container
8. Render pings /api/v1/health
9. deploy.yml verifies health from GitHub
10. Deployment complete
```

### 14.4.6 Migration in Deployment

Render runs the container as-is. To run migrations, the container's
start command must run them before starting uvicorn.

**Option A: Entrypoint script**

```bash
#!/bin/sh
set -e
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Option B: CMD chain**

```dockerfile
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

The project uses Option B for simplicity.

### 14.4.7 First Deployment Steps

1. Create a Render account (no credit card).
2. Create a new Blueprint from the repository.
3. Render reads `render.yaml` and creates the service and database.
4. Wait for the first deploy to complete.
5. Verify the health endpoint.
6. Configure UptimeRobot.

### 14.4.8 Subsequent Deployments

Pushes to main trigger the pipeline automatically. No manual action
is needed unless the deploy is triggered from the Render dashboard.

## 14.5 Cold Start Mitigation

### 14.5.1 Problem

Render free tier sleeps the service after 15 minutes of inactivity.
The next request takes 30-60 seconds to respond.

### 14.5.2 Mitigation: UptimeRobot

UptimeRobot pings the health endpoint every 10 minutes. This keeps the
service from sleeping for most of the day.

| Setting | Value |
|---|---|
| Monitor type | HTTP(s) |
| URL | https://expense-tracker-dashboard.onrender.com/api/v1/health |
| Interval | 10 minutes |
| Alert | Email on down |
| Expected status | 200 |

### 14.5.3 README Notice

The README includes a note:

```markdown
## Live Demo

URL: https://expense-tracker-dashboard.onrender.com

Note: This app runs on Render's free tier. The service sleeps after
15 minutes of inactivity. The first request after sleep may take up
to 60 seconds. UptimeRobot pings every 10 minutes to minimize this.
```

### 14.5.4 Peer Review Consideration

Peer reviewers are asked to open the URL early and wait for the first
load. Subsequent requests are fast.

## 14.6 Rollback

### 14.6.1 Rollback Procedure

1. Open the Render dashboard.
2. Navigate to the service.
3. Click "Deploys".
4. Find the previous successful deploy.
5. Click "Redeploy".

The service restarts with the previous image.

### 14.6.2 Rollback Triggers

| Trigger | Action |
|---|---|
| Health check fails after deploy | Rollback |
| E2E smoke test fails manually | Rollback |
| Users report broken feature | Assess, rollback if needed |
| Fallback unexpectedly active | Investigate |

### 14.6.3 Database Rollback

Migrations are forward-only. To roll back a migration:

1. Revert the code change.
2. Write a new migration that undoes the schema change.
3. Deploy.

Direct `alembic downgrade` in production is not part of the workflow.

### 14.6.4 Limitations

| Limitation | Impact |
|---|---|
| Manual rollback | Requires dashboard access |
| No automated rollback | Human decision required |
| No canary | All users affected at once |
| No blue-green | Brief downtime during restart |

## 14.7 Deployment Verification

### 14.7.1 Automatic Verification

`deploy.yml` verifies the health endpoint after deployment. If health
fails, the workflow fails and the team is notified.

### 14.7.2 Manual Verification

After deployment, run through the smoke test:

| Step | Expected |
|---|---|
| Open the URL | Login page appears |
| Register a new user | Redirects to dashboard |
| Add an expense | Appears in the list |
| Set a budget | Saves successfully |
| Dashboard | All 5 charts render |
| Switch month | Charts update |
| Logout | Redirects to login |

Results are recorded in `ops/deployment-health.md`.

### 14.7.3 Verification Record

Each deployment records:

- Date
- Commit hash
- Health response
- Smoke test results
- Screenshots
- Notes

## 14.8 Security in CI/CD

### 14.8.1 Secrets

| Secret | Stored In | Used By |
|---|---|---|
| RENDER_DEPLOY_HOOK | GitHub Actions secrets | deploy.yml |
| JWT_SECRET | Render environment | Backend |
| DATABASE_URL | Render environment | Backend |

No secrets are stored in the repository.

### 14.8.2 Permissions

GitHub Actions workflows use the default `GITHUB_TOKEN` with minimal
permissions. No long-lived AWS credentials are used.

### 14.8.3 Supply Chain

| Control | Implementation |
|---|---|
| Pinned action versions | `actions/checkout@v4`, `actions/setup-node@v4` |
| Locked dependencies | `uv.lock`, `package-lock.json` |
| Dependabot | Not enabled in MVP (documented) |
| Trivy scan | Run locally before deploy |

### 14.8.4 Not in CI

Security scans are not run in CI, per the project decision. They are
run locally and the results are committed to `security/`.

## 14.9 CI/CD Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| CI provider | GitHub Actions | Free, integrated, course-aligned |
| Test split | Backend and frontend in parallel | Faster feedback |
| Integration tests | In ci.yml | Catch contract issues early |
| E2E timing | On main only | Saves CI minutes |
| Deploy trigger | After E2E passes | Ensures quality before deploy |
| Deploy method | Render deploy hook | Simple, reliable |
| Health verification | Post-deploy curl | Catches broken deploys |
| Migration | Runs in container CMD | Simple, automatic |
| Container | Single app container | Simpler than separate frontend |
| Base images | Pinned tags | Reproducible builds |
| Non-root user | Yes | Security best practice |
| Cold start | UptimeRobot | Free mitigation |
| Rollback | Manual via Render | Simple, effective |
| Security scans | Local only | Project decision |
| Secrets | GitHub + Render env | Never in repo |
```

---
