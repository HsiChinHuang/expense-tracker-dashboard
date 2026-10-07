# Chapter 15: Documentation

## 15.1 Overview

Documentation is a scored artifact. This chapter defines every
document in the repository, what it contains, and why it exists. It
maps to Criteria 1, 2, 12, 13, and 14.

### 15.1.1 Documentation Principles

| Principle | Explanation |
|---|---|
| English only | All docs are in English for international reviewers |
| One purpose per file | Each document has a clear scope |
| Reviewer-first | A reviewer should find evidence quickly |
| Living documents | Updated when corrections are made |
| Linked, not duplicated | AGENTS.md links to docs rather than inlining |
| Short where possible | AGENTS.md is minimal; details live in docs/ |

### 15.1.2 Documentation Map

```
Repository root
├── README.md              Entry point for reviewers
├── product-spec.md        Full product specification
├── AGENTS.md              Agent context (short)
├── CLAUDE.md              Points to AGENTS.md
├── openapi.yaml           API contract
├── LICENSE                MIT
│
├── docs/                  Detailed documentation
│   ├── architecture.md
│   ├── api.md
│   ├── process.md
│   ├── ai-workflow.md
│   ├── design-system.md
│   ├── testing-guidelines.md
│   ├── agent-extension-pack.md
│   ├── permissions.md
│   ├── task-template.md
│   └── team/
│       ├── pm.md
│       ├── software-engineer.md
│       └── qa-engineer.md
│
├── security/              Security artifacts
│   ├── pr-audit.md
│   ├── gitleaks-report.json
│   ├── semgrep-report.json
│   ├── trivy-report.json
│   ├── pip-audit-report.txt
│   ├── npm-audit-report.txt
│   ├── agent-security-notes.md
│   └── ai-tool-data-policy.md
│
├── ops/                   Operations artifacts
│   ├── runbook.md
│   ├── health-check.md
│   ├── diagnosis.md
│   ├── logging.md
│   └── deployment-health.md
│
└── screenshots/           UI screenshots
    ├── dashboard.png
    ├── expense-form.png
    ├── budget-page.png
    └── health-check.png
```

## 15.2 Root-Level Documents

### 15.2.1 README.md

**Purpose**: Entry point for reviewers. First file a reviewer reads.

**Length**: Under 500 lines.

**Sections**:

| Section | Content |
|---|---|
| Title and tagline | Project name, one-line description |
| Live demo | URL and cold-start note |
| Features | Bullet list of core features |
| Tech stack | Table of technologies |
| Architecture | High-level diagram, link to docs/architecture.md |
| Quick start | Prerequisites, two setup options |
| Running tests | Make targets |
| API documentation | Link to openapi.yaml and /docs |
| AI-assisted development | Brief note, link to docs/ai-workflow.md |
| Agent extension pack | Brief note, links to directories |
| Security | Link to security/ |
| Operations | Link to ops/ |
| Final Project criteria mapping | Table mapping criteria to evidence |
| Project structure | Directory tree |
| License | MIT |

**Example structure**:

```markdown
# Expense Tracker & Budget Dashboard

A full-stack personal finance application for tracking expenses and
managing monthly budgets.

## Live Demo

- URL: https://expense-tracker-dashboard.onrender.com
- Note: Free tier cold start takes ~30-60 seconds

## Features

- User registration and JWT authentication
- Expense CRUD with categories
- Monthly budget setting
- Dashboard with 5 visualizations
- Custom categories with colors
- Audit logging
- SQLite automatic fallback when PostgreSQL is unavailable

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind, Recharts |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| Database | PostgreSQL (prod), SQLite (local/fallback) |
| Auth | JWT (HS256) + bcrypt |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render |
| E2E | Playwright |

## Architecture

See `docs/architecture.md`.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12+ and uv (for local backend dev)

### Option 1: Full Docker

```bash
git clone https://github.com/<user>/expense-tracker-dashboard.git
cd expense-tracker-dashboard
cp .env.example .env
docker compose up --build
```

Open http://localhost:8000

### Option 2: Hybrid

```bash
# Terminal 1: database
docker compose up db

# Terminal 2: backend
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Terminal 3: frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Running Tests

```bash
make test           # all unit tests
make test-backend   # pytest
make test-frontend  # vitest
make e2e            # Playwright
```

## API Documentation

- OpenAPI spec: `openapi.yaml`
- Interactive docs: http://localhost:8000/docs

## AI-Assisted Development

Built with pi-agent + qwen3.8-27b local model.
See `docs/ai-workflow.md`.

## Agent Extension Pack

- Skills: `agent-capabilities/`
- Hooks: `agent-hooks/`
- MCP server: `mcp-server/`
- Subagents: `custom-agent/`
- Permissions: `docs/permissions.md`
- Overview: `docs/agent-extension-pack.md`

## Security

Scan artifacts in `security/`.
Agent security notes in `security/agent-security-notes.md`.

## Operations

See `ops/runbook.md` for troubleshooting.
Health check: `/api/v1/health`

## Final Project Criteria Mapping

| Criterion | Where to Find Evidence |
|---|---|
| 1. Problem Description | README, product-spec.md |
| 2. AI Workflow | docs/ai-workflow.md, AGENTS.md, docs/process.md |
| 3. Architecture | docs/architecture.md |
| 4. Frontend | frontend/, README test commands |
| 5. API Contract | openapi.yaml |
| 6. Backend | backend/, backend/tests/ |
| 7. Database | backend/alembic/, docs/architecture.md |
| 8. Containerization | docker-compose.yml, Dockerfile |
| 9. Integration Testing | e2e/, backend/tests/integration/ |
| 10. Deployment | Live URL, render.yaml, ops/deployment-health.md |
| 11. CI/CD | .github/workflows/ |
| 12. Agent Extension Pack | agent-capabilities/, agent-hooks/, mcp-server/, custom-agent/, docs/agent-extension-pack.md, docs/permissions.md |
| 13. Security/Audit/DevOps | security/, ops/ |
| 14. Reproducibility | README Quick Start, Makefile, .env.example |

## Project Structure

```
expense-tracker-dashboard/
├── frontend/    React SPA
├── backend/     FastAPI application
├── e2e/         Playwright tests
├── docs/        Documentation
├── security/    Security artifacts
├── ops/         Operations artifacts
├── agent-capabilities/  Skills
├── agent-hooks/         Guardrails
├── mcp-server/          MCP tools
├── custom-agent/        Subagents
└── screenshots/         UI screenshots
```

## License

MIT
```

### 15.2.2 product-spec.md

**Purpose**: Complete product specification.

**Length**: 500-800 lines.

**Sections**: Mirrors Chapter 2.

| Section | Content |
|---|---|
| Problem statement | Why this exists |
| Target users | Who it is for |
| User stories | Numbered, by feature area |
| Functional requirements | Detailed behavior per endpoint |
| Non-functional requirements | Performance, security, usability |
| Edge cases | Exhaustive list |
| Success criteria | Measurable targets |
| Scope boundaries | In scope, out of scope |

### 15.2.3 AGENTS.md

**Purpose**: Context for the coding agent. Read at every session start.

**Length**: Under 60 lines.

**Content**: Commands, rules, document links. See Chapter 9 for the
full content.

### 15.2.4 CLAUDE.md

**Purpose**: Compatibility with Claude Code.

**Content**: One line.

```
@AGENTS.md
```

### 15.2.5 openapi.yaml

**Purpose**: API contract. Single source of truth for API shapes.

**Content**: Full OpenAPI 3.1 specification. See Chapter 7.

### 15.2.6 LICENSE

**Purpose**: Legal terms.

**Content**: MIT license text.

## 15.3 docs/ Documents

### 15.3.1 docs/architecture.md

**Purpose**: Explain the system architecture in detail.

**Sections**:

| Section | Content |
|---|---|
| Overview | Three-tier architecture plus agent layer |
| Diagram | High-level diagram |
| Frontend | Layers, data flow, state ownership |
| Backend | Layers, request lifecycle, transactions |
| Database | Engine selection, fallback logic |
| Authentication | JWT flow |
| Directory structure | Full tree |
| Cross-cutting concerns | Logging, config, errors |
| Architectural decisions | Table of choices and rationale |

**Reference**: Mirrors Chapter 4.

### 15.3.2 docs/api.md

**Purpose**: Practical API usage guide.

**Sections**:

| Section | Content |
|---|---|
| Base URL | Local and production |
| Authentication | How to get and use a token |
| Common patterns | Pagination, error format, amounts |
| Endpoint reference | Grouped by resource |
| Examples | curl examples for common operations |
| Error codes | Full list |

**Example**:

```markdown
## Authentication

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'
```

Response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": "...", "email": "...", "username": "..." }
}
```

### Using the token

```bash
curl http://localhost:8000/api/v1/expenses \
  -H "Authorization: Bearer eyJ..."
```
```

### 15.3.3 docs/process.md

**Purpose**: Define the workflow and roles.

**Content**: Mirrors Chapter 9 sections 9.5.1. Roles, orchestrator,
lifecycle, rules.

### 15.3.4 docs/ai-workflow.md

**Purpose**: Document how AI tools were used. Required for Criterion 2.

**Sections**:

| Section | Content |
|---|---|
| Tools used | pi-agent, qwen3.8-27b, plugins |
| Workflow overview | Spec → backlog → PM → SWE → QA |
| Context engineering | AGENTS.md, docs/, skills |
| Roles | PM, SWE, QA |
| Orchestration | Main session enforces the graph |
| Example prompts | Table of prompts and outcomes |
| Session records | Real sessions with dates |
| Correction log | Mistakes and fixes |
| Skills used | Three skills |
| Subagents used | Two subagents |
| MCP tools | Four tools |
| Review process | Human review steps |
| Data policy | Link to security/ai-tool-data-policy.md |

**Session record format**: See Chapter 9, section 9.12.2.

### 15.3.5 docs/design-system.md

**Purpose**: UI conventions so the interface does not drift between
sessions.

**Sections**:

| Section | Content |
|---|---|
| Colors | Tokens and values |
| Typography | Sizes, weights, font |
| Spacing | Scale and usage |
| Components | Button, Card, Input, Modal, Toast |
| Chart colors | Per chart |
| States | Loading, empty, error |
| Accessibility | Checklist |

**Reference**: Mirrors Chapter 8, section 8.10.

### 15.3.6 docs/testing-guidelines.md

**Purpose**: Rules for writing tests.

**Sections**:

| Section | Content |
|---|---|
| Test layers | Unit, integration, E2E |
| Backend rules | Fixtures, isolation, Decimal |
| Frontend rules | RTL queries, MSW |
| E2E rules | Unique users, no cleanup |
| Coverage policy | Reported, not enforced |
| Naming conventions | `test_<behavior>` |
| What not to test | Implementation details |

**Example rules**:

```markdown
## Backend Test Rules

- Use the `db_session` fixture for all tests that touch the database.
- Never use `float` for amounts; use `Decimal`.
- Every endpoint that reads user data must have an isolation test.
- Assert on status code and error code for error cases.
- Use fixed dates (e.g., `date(2026, 10, 15)`) for determinism.

## Frontend Test Rules

- Query by role or label, not by test ID, where possible.
- Mock API with MSW, not by mocking axios.
- Test behavior, not implementation.
- Chart tests assert on color classes, not SVG paths.

## E2E Rules

- Each test registers its own user.
- Do not clean the database between tests.
- Use `data-testid` for elements that are hard to select by role.
- Assert on visible text, not internal state.
```

### 15.3.7 docs/agent-extension-pack.md

**Purpose**: Overview of the Agent Extension Pack.

**Reference**: Mirrors Chapter 10, section 10.6.2.

### 15.3.8 docs/permissions.md

**Purpose**: Permission matrix for users, agents, and tools.

**Reference**: Mirrors Chapter 10, section 10.7.1.

### 15.3.9 docs/task-template.md

**Purpose**: Template for grooming issues.

**Content**:

```markdown
## Goal

One or two sentences on what should be true when this is done.

## Acceptance criteria

- [ ] A statement you can check by looking at the result
- [ ] One line per case, including the awkward ones

## Out of scope

- Something that does not belong in this task, moved to #TASK-NUMBER

## Constraints

- Files this should stay inside
- Libraries to use
- Guidelines to follow
```

### 15.3.10 docs/team/pm.md

**Purpose**: PM agent role definition.

**Reference**: Mirrors Chapter 9, section 9.4.1.

### 15.3.11 docs/team/software-engineer.md

**Purpose**: SWE agent role definition.

**Reference**: Mirrors Chapter 9, section 9.4.2.

### 15.3.12 docs/team/qa-engineer.md

**Purpose**: QA agent role definition.

**Reference**: Mirrors Chapter 9, section 9.4.3.

## 15.4 security/ Documents

| File | Purpose | Required By |
|---|---|---|
| pr-audit.md | PR review with AI assistance | Criterion 13 |
| gitleaks-report.json | Secret scan output | Criterion 13 |
| semgrep-report.json | SAST output | Criterion 13 |
| trivy-report.json | Dependency and image scan | Criterion 13 |
| pip-audit-report.txt | Python dependency scan | Criterion 13 |
| npm-audit-report.txt | Node dependency scan | Criterion 13 |
| agent-security-notes.md | Agent security design | Criterion 13 |
| ai-tool-data-policy.md | AI data policy | Criterion 13 |

**Reference**: Mirrors Chapter 12.

## 15.5 ops/ Documents

| File | Purpose | Required By |
|---|---|---|
| runbook.md | Common problems and diagnosis | Criterion 13 |
| health-check.md | Health endpoint reference | Criterion 13 |
| diagnosis.md | Worked diagnosis example | Criterion 13 |
| logging.md | Log format and events | Criterion 13 |
| deployment-health.md | Deployment verification record | Criterion 10 |

**Reference**: Mirrors Chapter 13.

## 15.6 screenshots/ Directory

### 15.6.1 Purpose

Screenshots make the README more convincing and give reviewers visual
evidence that the app works.

### 15.6.2 Contents

| File | Shows |
|---|---|
| dashboard.png | The dashboard with all 5 charts and KPI cards |
| expense-form.png | The expense creation modal |
| budget-page.png | The budget page |
| health-check.png | The health endpoint response |

### 15.6.3 How They Are Used

| Location | Usage |
|---|---|
| README.md | Embedded in the Features section |
| ops/deployment-health.md | Referenced as deployment evidence |

### 15.6.4 Guidelines

- Capture at a consistent viewport size (e.g., 1440x900)
- Use realistic seed data, not "test test test"
- Blur or omit any real personal data
- Keep file size reasonable (< 500 KB each)

## 15.7 .env.example

**Purpose**: Template for environment variables.

**Content**:

```bash
# Backend
DATABASE_URL=postgresql://expense:expense@localhost:5432/expense
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_ISSUER=expense-tracker
JWT_AUDIENCE=expense-tracker-api
CORS_ORIGINS=["http://localhost:5173"]
ENVIRONMENT=development
APP_VERSION=1.0.0

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# MCP Server
MCP_API_BASE_URL=http://localhost:8000/api/v1
MCP_JWT_SECRET=${JWT_SECRET}
MCP_USER_TOKEN=
```

**Rules**:

- This file is committed.
- The real `.env` is in `.gitignore`.
- No real secrets are in `.env.example`.

## 15.8 Makefile

**Purpose**: Single entry point for common commands.

**Content**:

```makefile
.PHONY: dev down test test-backend test-frontend e2e lint migrate seed security

dev:
	docker compose up --build

down:
	docker compose down

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest -v

test-frontend:
	cd frontend && npm run test -- --run

e2e:
	docker compose up -d --build
	cd e2e && npm ci && npx playwright test
	docker compose down

lint:
	cd backend && uv run ruff check .
	cd frontend && npm run lint

migrate:
	cd backend && uv run alembic upgrade head

seed:
	cd backend && uv run python -m app.scripts.seed

security:
	gitleaks detect --source . --report-format json --report-path security/gitleaks-report.json
	semgrep --config=auto --json --output=security/semgrep-report.json
	cd backend && pip-audit --format json > ../security/pip-audit-report.txt
	cd frontend && npm audit --json > ../security/npm-audit-report.txt
```

## 15.9 Documentation Guidelines

### 15.9.1 Writing Rules

| Rule | Reason |
|---|---|
| English only | International reviewers |
| Present tense | "The app returns..." not "The app will return..." |
| Active voice | "The service filters..." not "The data is filtered..." |
| Short paragraphs | Easier to scan |
| Tables for comparisons | Compact and clear |
| Code blocks for commands | Copy-paste friendly |
| No marketing language | Direct, factual |
| No emojis | Professional tone |
| No screenshots in docs/ | Keep docs text-only; images in screenshots/ |

### 15.9.2 Linking Rules

| Rule | Reason |
|---|---|
| Link, do not duplicate | Avoids drift |
| Relative links | Works on GitHub and locally |
| Link text is descriptive | "See docs/architecture.md" not "click here" |
| Every document is linked from somewhere | No orphans |

### 15.9.3 Updating Rules

| Trigger | Action |
|---|---|
| Correction during a session | Update the relevant document |
| New decision | Update the architecture or process doc |
| New skill | Update agent-extension-pack.md |
| New permission | Update permissions.md |
| New error code | Update api.md and openapi.yaml |

### 15.9.4 Document Ownership

| Document | Updated By |
|---|---|
| README.md | Human |
| product-spec.md | Human, PM agent |
| AGENTS.md | Human |
| docs/architecture.md | Human, SWE agent |
| docs/api.md | SWE agent |
| docs/process.md | Human |
| docs/ai-workflow.md | Human |
| docs/design-system.md | Human, SWE agent |
| docs/testing-guidelines.md | Human, QA agent |
| docs/agent-extension-pack.md | Human |
| docs/permissions.md | Human |
| security/*.md | Human |
| ops/*.md | Human |

## 15.10 Reviewer Quick Path

A reviewer should be able to verify the project in 10 minutes.

### 15.10.1 5-Minute Live Verification

1. Open the live URL (wait for cold start)
2. Register a new user
3. Add an expense
4. Set a budget
5. Check that the dashboard renders all 5 charts
6. Switch the month
7. Log out

### 15.10.2 5-Minute Local Verification

```bash
git clone <repo>
cd expense-tracker-dashboard
cp .env.example .env
docker compose up --build
```

Open http://localhost:8000 and repeat the live verification steps.

### 15.10.3 Evidence Checklist

| Criterion | File to Open |
|---|---|
| 1 | README.md, product-spec.md |
| 2 | docs/ai-workflow.md, docs/process.md |
| 3 | docs/architecture.md |
| 4 | frontend/, `make test-frontend` |
| 5 | openapi.yaml |
| 6 | backend/, `make test-backend` |
| 7 | backend/alembic/, docs/architecture.md |
| 8 | Dockerfile, docker-compose.yml |
| 9 | e2e/, backend/tests/integration/ |
| 10 | Live URL, ops/deployment-health.md |
| 11 | .github/workflows/ |
| 12 | agent-capabilities/, agent-hooks/, mcp-server/, custom-agent/, docs/agent-extension-pack.md, docs/permissions.md |
| 13 | security/, ops/ |
| 14 | README Quick Start, Makefile, .env.example |

## 15.11 Documentation Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Language | English only | International reviewers |
| Root docs | Minimal, essential only | Keeps the root clean |
| Detail location | docs/ | Separates overview from detail |
| README length | Under 500 lines | Scannable |
| AGENTS.md length | Under 60 lines | Fits in agent context |
| Criteria mapping | In README | Reviewers find evidence fast |
| Screenshots | In screenshots/ | Visual evidence without bloating docs |
| No peer-review-guide.md | Merged into README | Avoids extra file |
| No CHANGELOG | Git history is the record | Simpler |
| No CONTRIBUTING | Single-author project | Not needed |
| No CODE_OF_CONDUCT | Not applicable | Not needed |
| API docs | openapi.yaml + /docs | Contract plus interactive view |
| Diagrams | ASCII in markdown | No external image dependencies |
| Code blocks | Fenced with language | Syntax highlighting |
| Tables | Used for comparisons | Compact |
| No emojis | Professional tone | Consistency |
```

---