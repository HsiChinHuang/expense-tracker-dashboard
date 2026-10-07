# Chapter 3: Tech Stack

## 3.1 Frontend

### 3.1.1 Core

| Technology | Version | Role | Why This Choice |
|---|---|---|---|
| React | 18.x | UI framework | Industry standard, largest ecosystem, course uses it in Part 2 |
| TypeScript | 5.x | Type safety | Catches errors at compile time, better IDE support, self-documenting APIs |
| Vite | 5.x | Build tool and dev server | Fast HMR, native ESM, simple config, used in course Part 2 |
| React Router | 6.x | Client-side routing | Standard for React SPAs, supports nested routes and route guards |
| Tailwind CSS | 3.x | Styling | Utility-first, no runtime overhead, consistent design tokens, fast to build attractive UI |
| Recharts | 2.x | Charts | React-native charting, composable, good TypeScript support, covers all 5 chart types |
| TanStack Query | 5.x | Server state management | Caching, retries, loading/error states, invalidation — removes boilerplate |
| React Hook Form | 7.x | Form state | Minimal re-renders, easy integration with Zod |
| Zod | 3.x | Schema validation | TypeScript-first, shared validation logic between form and API |
| Axios | 1.x | HTTP client | Interceptors for auth token and error handling, widely used |
| date-fns | 3.x | Date utilities | Lightweight, tree-shakeable, immutable, no timezone surprises |

### 3.1.2 Development Dependencies

| Technology | Version | Role |
|---|---|---|
| Vitest | 1.x | Unit and component testing |
| React Testing Library | 14.x | Component testing utilities |
| MSW | 2.x | API mocking in tests |
| ESLint | 8.x | Linting |
| Prettier | 3.x | Code formatting |
| TypeScript ESLint | 7.x | TypeScript-specific lint rules |

### 3.1.3 Why Not Other Choices

| Rejected | Reason |
|---|---|
| Next.js | Overkill for a SPA; SSR not needed; adds complexity |
| Redux | Too much boilerplate; React Query + Context is sufficient |
| Chart.js | Less React-native than Recharts; more imperative |
| Material UI | Heavy; harder to customize; Tailwind gives more control |
| Create React App | Deprecated; Vite is faster and better maintained |
| Styled Components | Runtime overhead; Tailwind is faster |
| Formik | More re-renders than React Hook Form; larger bundle |
| SWR | React Query has more features (invalidation, mutations) |

## 3.2 Backend

### 3.2.1 Core

| Technology | Version | Role | Why This Choice |
|---|---|---|---|
| Python | 3.12 | Language | Modern, stable, good async support, course uses it |
| FastAPI | 0.110+ | Web framework | Auto-generated OpenAPI, async, Pydantic integration, course uses it in Part 2 |
| SQLAlchemy | 2.0 | ORM | Supports both PostgreSQL and SQLite, mature, type-safe queries |
| Alembic | 1.13+ | Database migrations | Standard for SQLAlchemy, version-controlled schema |
| Pydantic | 2.x | Validation and serialization | FastAPI native, Decimal support, clear error messages |
| python-jose | 3.3+ | JWT handling | Supports HS256, audience, issuer validation |
| passlib[bcrypt] | 1.7+ | Password hashing | Bcrypt with salt, widely used, secure defaults |
| uvicorn | 0.29+ | ASGI server | Fast, production-ready, standard for FastAPI |
| uv | Latest | Dependency management | Fast, course uses it in Part 2, replaces pip + venv |
| httpx | 0.27+ | HTTP client | Async, used for testing and MCP server |

### 3.2.2 Development Dependencies

| Technology | Version | Role |
|---|---|---|
| pytest | 8.x | Test framework |
| pytest-cov | 5.x | Coverage reporting |
| pytest-asyncio | 0.23+ | Async test support |
| ruff | 0.4+ | Linting and formatting |
| mypy | 1.10+ | Static type checking |

### 3.2.3 Why Not Other Choices

| Rejected | Reason |
|---|---|
| Django | Heavier, includes ORM and admin we don't need, slower startup |
| Flask | No built-in OpenAPI, more manual work |
| Pyramid | Less community, steeper learning curve |
| Tortoise ORM | Less mature, smaller community than SQLAlchemy |
| PyJWT | python-jose has audience/issuer validation built in |
| Argon2 | Bcrypt is simpler and sufficient for this project |
| Poetry | uv is faster and course uses it |
| pip-tools | uv replaces it |

## 3.3 Database

### 3.3.1 Strategy

| Environment | Database | Reason |
|---|---|---|
| Local development (default) | SQLite | Zero configuration, fast startup, file-based |
| Local development (Docker Compose) | PostgreSQL 16 | Matches production, tests real behavior |
| Production (Render) | PostgreSQL 16 | Free tier available, managed, real database |
| Fallback (automatic) | SQLite | Keeps app functional when PostgreSQL is unreachable |

### 3.3.2 Why This Strategy

- **SQLite for local**: New developers can run the backend without Docker
- **PostgreSQL for Compose**: Tests real database behavior before deploying
- **PostgreSQL for production**: Real persistence, real constraints, real performance
- **SQLite fallback**: Render free PostgreSQL expires after 30 days; fallback
  ensures peer reviewers can always use the app

### 3.3.3 PostgreSQL 16

| Feature | Use in This Project |
|---|---|
| NUMERIC(12,2) | Expense and budget amounts |
| DATE | Expense dates |
| TIMESTAMPTZ | Created/updated timestamps |
| JSONB | Audit log old/new values |
| UUID | Primary keys |
| CHECK constraints | Amount > 0, valid action types |
| UNIQUE constraints | Email, username, (user_id, year_month) |
| Foreign keys | user_id, category_id |
| Indexes | user_id, date, category_id, year_month |

### 3.3.4 SQLite

| Feature | Use in This Project |
|---|---|
| NUMERIC | Stored as REAL, but SQLAlchemy handles Decimal conversion |
| DATE | Stored as TEXT in ISO format |
| JSON | Stored as TEXT, SQLAlchemy serializes |
| UUID | Stored as TEXT |
| CHECK constraints | Supported |
| UNIQUE constraints | Supported, but NULL handling differs |
| Foreign keys | Supported when PRAGMA foreign_keys = ON |
| Indexes | Supported |

**SQLite-specific handling**:
- Enable foreign keys: `PRAGMA foreign_keys = ON` on every connection
- Use `check_same_thread: False` for FastAPI async
- Avoid PostgreSQL-specific functions (e.g., `to_char`, `gen_random_uuid`)
- Use Python-side UUID generation instead of database default

### 3.3.5 Database Abstraction

All database access goes through SQLAlchemy. No raw SQL except in migrations.
This ensures:

- Switching between SQLite and PostgreSQL requires only changing the URL
- Tests can use SQLite in-memory for speed
- Production uses PostgreSQL without code changes

**Functions that differ between databases**:

| Need | PostgreSQL | SQLite | Solution |
|---|---|---|---|
| Extract year-month | `to_char(date, 'YYYY-MM')` | `strftime('%Y-%m', date)` | Use Python post-processing |
| UUID generation | `gen_random_uuid()` | Not available | Generate in Python |
| JSON operations | JSONB operators | JSON functions | Store as text, parse in Python |
| Case-insensitive search | ILIKE | LIKE (case-insensitive by default) | Use lower() on both sides |

## 3.4 Containerization

### 3.4.1 Docker

| Component | Image | Purpose |
|---|---|---|
| Frontend build stage | node:20-alpine | Compile React app to static files |
| Backend runtime | python:3.12-slim | Run FastAPI with uv |
| Database (Compose only) | postgres:16-alpine | Local development database |

### 3.4.2 Docker Compose

| Service | Purpose | Port |
|---|---|---|
| db | PostgreSQL for local development | 5432 |
| app | Full-stack application (backend serves frontend) | 8000 |

**Why single container for app**: In production, the frontend is static files
served by FastAPI. There is no need for a separate frontend container. This
matches the course Part 3 approach.

**Why separate db service**: PostgreSQL runs as its own service in Compose
so developers can restart the app without losing data.

### 3.4.3 Why Not Other Choices

| Rejected | Reason |
|---|---|
| Kubernetes | Overkill for a single-container app |
| Separate frontend container | Unnecessary in production; static files served by backend |
| Nginx as reverse proxy | FastAPI can serve static files; no need for extra layer locally |
| Podman | Docker is more widely supported |

## 3.5 CI/CD

### 3.5.1 GitHub Actions

| Workflow | Trigger | Purpose |
|---|---|---|
| ci.yml | Pull request, push to main | Lint, unit tests, integration tests |
| e2e.yml | Push to main | Build Docker Compose, run Playwright |
| deploy.yml | After e2e.yml succeeds | Deploy to Render, verify health |

### 3.5.2 Why GitHub Actions

- Free for public repositories
- Native integration with GitHub
- Course uses it in Part 3
- No external CI service needed

### 3.5.3 Why Not Other Choices

| Rejected | Reason |
|---|---|
| GitLab CI | Not using GitLab |
| CircleCI | Free tier limited, external service |
| Jenkins | Self-hosted, complex setup |
| Travis CI | Free tier discontinued |
| AWS CodePipeline | More complex, AWS-specific |

## 3.6 Deployment

### 3.6.1 Platform

| Platform | Plan | Cost | Why |
|---|---|---|---|
| Render | Free | $0 | No credit card required, free PostgreSQL, free web service, simple Docker deployment |

### 3.6.2 Render Free Tier Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| Web service sleeps after 15 min idle | First request takes 30-60s | UptimeRobot ping every 10 min |
| PostgreSQL expires after 30 days | Data loss mid-review | SQLite automatic fallback |
| 512 MB RAM, 0.1 CPU | Limited concurrency | Acceptable for demo and peer review |
| No SSH access | Cannot debug directly | Use Render logs |
| No persistent disk | File writes lost on restart | Not used for persistence |
| 750 hours/month | Enough for one service | Only one service running |
| 5 GB bandwidth/month | Enough for demo traffic | Charts are SVG, minimal data |
| 500 build minutes/month | Enough for ~100 deploys | CI runs separately on GitHub |

### 3.6.3 Why Not Other Choices

| Rejected | Reason |
|---|---|
| AWS EC2 | Costs money, complex setup, course Part 3 uses it but overkill here |
| Fly.io | Requires credit card even for free tier |
| Railway | $1/month free credit insufficient for full stack |
| Heroku | Free tier discontinued |
| Vercel | Serverless, not suitable for FastAPI + PostgreSQL |
| Netlify | Static only, no backend |
| Supabase | Adds external dependency; we chose PostgreSQL on Render |
| Neon | Adds external dependency; user preferred not to |

## 3.7 Development Tools

### 3.7.1 AI Coding Agent

| Tool | Role |
|---|---|
| pi-agent | Primary coding agent |
| qwen3.8-27b | Local LLM for pi-agent |
| Plugins | Added as needed for missing capabilities |

**Capabilities confirmed**:
- Reads AGENTS.md
- Discovers skills
- Launches subagents
- Tool use (function calling)
- File operations (read, write, edit)
- Command execution

**Data policy**: All code, prompts, and context stay on the local machine.
No data is sent to cloud LLM providers. See `security/ai-tool-data-policy.md`.

### 3.7.2 Version Control

| Tool | Role |
|---|---|
| Git | Version control |
| GitHub | Remote repository, Issues, Actions |
| Conventional Commits | Commit message format |
| Feature branches | Branch strategy |

### 3.7.3 Code Quality

| Tool | Role |
|---|---|
| ruff (backend) | Lint and format Python |
| ESLint (frontend) | Lint TypeScript and React |
| Prettier (frontend) | Format TypeScript, CSS, JSON |
| mypy (backend) | Static type checking |
| TypeScript compiler | Type checking frontend |

### 3.7.4 Security Scanning

| Tool | Purpose | When |
|---|---|---|
| gitleaks | Detect secrets in git history | Before deploy |
| semgrep | Static analysis for security issues | Before deploy |
| trivy | Scan dependencies and Docker images | Before deploy |
| pip-audit | Audit Python dependencies | Before deploy |
| npm audit | Audit Node dependencies | Before deploy |

All scans are run locally and results are committed to `security/`.

### 3.7.5 Testing

| Tool | Purpose |
|---|---|
| pytest | Backend unit and integration tests |
| Vitest | Frontend unit and component tests |
| React Testing Library | Component testing |
| MSW | API mocking |
| Playwright | End-to-end testing |
| httpx | Backend API testing |

### 3.7.6 Monitoring

| Tool | Purpose |
|---|---|
| Render logs | Application logs |
| Health check endpoint | Database and app status |
| UptimeRobot | Keep Render service warm |

## 3.8 Technology Summary Table

| Layer | Technology | Version |
|---|---|---|
| Frontend framework | React | 18.x |
| Frontend language | TypeScript | 5.x |
| Frontend build | Vite | 5.x |
| Frontend styling | Tailwind CSS | 3.x |
| Frontend charts | Recharts | 2.x |
| Frontend state | TanStack Query | 5.x |
| Frontend routing | React Router | 6.x |
| Frontend forms | React Hook Form + Zod | 7.x / 3.x |
| Frontend HTTP | Axios | 1.x |
| Frontend dates | date-fns | 3.x |
| Frontend tests | Vitest + RTL | 1.x / 14.x |
| Backend language | Python | 3.12 |
| Backend framework | FastAPI | 0.110+ |
| Backend ORM | SQLAlchemy | 2.0 |
| Backend migrations | Alembic | 1.13+ |
| Backend validation | Pydantic | 2.x |
| Backend JWT | python-jose | 3.3+ |
| Backend password | passlib[bcrypt] | 1.7+ |
| Backend server | uvicorn | 0.29+ |
| Backend deps | uv | Latest |
| Backend tests | pytest | 8.x |
| Database (prod) | PostgreSQL | 16 |
| Database (local) | SQLite | 3.x |
| Database (fallback) | SQLite | 3.x |
| Container | Docker | Latest |
| Orchestration | Docker Compose | Latest |
| CI/CD | GitHub Actions | - |
| Deployment | Render | Free tier |
| E2E | Playwright | Latest |
| AI agent | pi-agent | Latest |
| AI model | qwen3.8-27b | - |
| Monitoring | UptimeRobot | Free tier |

## 3.9 Version Pinning Strategy

- **Backend**: `pyproject.toml` with `uv.lock` for reproducible builds
- **Frontend**: `package.json` with `package-lock.json` for reproducible builds
- **Docker images**: Pinned to specific tags (e.g., `python:3.12-slim`, `node:20-alpine`, `postgres:16-alpine`)
- **GitHub Actions**: Pinned to major versions (e.g., `actions/checkout@v4`)
- **No `latest` tags** in production Dockerfiles

## 3.10 Environment Variables

All configuration is via environment variables. See `.env.example` for the full list.

| Variable | Default | Required | Used By |
|---|---|---|---|
| DATABASE_URL | sqlite:///./dev.db | No | Backend |
| JWT_SECRET | - | Yes (production) | Backend, MCP |
| JWT_ALGORITHM | HS256 | No | Backend |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | No | Backend |
| JWT_ISSUER | expense-tracker | No | Backend |
| JWT_AUDIENCE | expense-tracker-api | No | Backend |
| CORS_ORIGINS | ["http://localhost:5173"] | No | Backend |
| ENVIRONMENT | development | No | Backend |
| APP_VERSION | 1.0.0 | No | Backend |
| DB_CONNECT_TIMEOUT | 5 | No | Backend |
| VITE_API_BASE_URL | http://localhost:8000/api/v1 | No | Frontend |
| MCP_API_BASE_URL | http://localhost:8000/api/v1 | No | MCP Server |
| MCP_JWT_SECRET | ${JWT_SECRET} | No | MCP Server |