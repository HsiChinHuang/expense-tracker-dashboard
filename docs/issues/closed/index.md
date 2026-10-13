# Closed issues

Runtime-maintained by Orchestrator.

| ID | Title | Closed At | Retries | Merge Commit |
|---|---|---|---|---|
| t0 | Repository skeleton per Chapter 16 structure |  | 0 | 1753fd0 |
| t1 | Backend skeleton (FastAPI + uv + pytest + ruff/mypy) |  | 0 | 792f644 |
| t2 | Frontend skeleton (Vite + React + TS + Tailwind + Vitest) |  | 1 | 4f89797 |
| t3 | Health check endpoint GET /api/v1/health |  | 0 | b3c5746 |
| t4 | Root configuration files (.env.example, Makefile, LICENSE, README) |  | 0 | 410ac3e |
| t5 | Database foundation - Settings, SQLAlchemy engine/session, Alembic wiring |  | 0 | 8e9fcb3 |
| t6 | User model and users-table Alembic migration |  | 0 | 17064fc |
| t7 | Auth primitives - bcrypt password hashing and HS256 JWT module |  | 0 | d189d2d |
| t8 | Register / login / me endpoints with auth service and get_current_user |  | 1 | 8298a0b |
| t9 | Frontend auth - axios client, AuthContext, route guards, login/register pages |  | 0 | 1a89838 |
| t10 | Category model, Alembic revision 002, idempotent system-category seed |  | 0 |  |
| t11 | Categories API - list/create/delete with system protection and access validator |  | 0 |  |
| t12 | Audit foundation - audit_logs model, Alembic 003, same-transaction logger, get_client_ip |  | 0 |  |
| t13 | Expenses vertical - model + Alembic 004, service, five endpoints, audit integration |  | 0 |  |
| t14 | Budgets vertical - model + Alembic 005, upsert/get/delete endpoints, audit integration |  | 0 |  |
| t15 | Cross-resource user-isolation and money-precision test suite |  | 0 |  |
| t16 | Frontend data layer - typed api modules, queryKeys, CRUD hooks, MSW handlers |  | 0 |  |
| t17 | ExpensesPage + ExpenseForm modal + ToastProvider (network-error presentation) |  | 0 |  |
| t18 | BudgetPage + CategoriesPage |  | 0 |  |
| t19 | Dashboard backend - dashboard_service helpers and six GET endpoints |  | 0 |  |
| t20 | Frontend dashboard data layer - MonthContext, dashboard api/hooks, EmptyState/ErrorState |  | 0 |  |
| t21 | Recharts admission and four chart components (pie, trend, cumulative, heatmap) |  | 0 |  |
| t22 | DashboardPage - MonthPicker, KPI cards, BudgetProgress, recent list, chart wiring, edge cases |  | 0 |  |
| t23 | Dashboard verification - REQ-PLAN-041 cross-checks, criteria rows, performance measurement |  | 0 |  |
| t24 | Containerization - multi-stage Dockerfile, docker-compose db+app, .dockerignore, README local modes |  | 0 |  |
| t25 | SQLite fallback - create_db_engine PostgreSQL timeout chain, fallback create_all + seed, live health reporting |  | 0 |  |
| t26 | CI/CD and Render - ci.yml e2e.yml deploy.yml workflows, render.yaml, Makefile test targets, README deploy notice |  | 0 |  |
| t27 | Playwright E2E harness - e2e workspace, config, fixtures, three specs, Makefile e2e target |  | 0 |  |
| t28 | Infra verification - criteria 8/10/11 + rows 29/30, fallback timing evidence, deferral register, full-suite composite |  | 0 |  |
| t29 | Skills layer - three SKILL.md documents, .agents/skills symlinks, canonical discovery gate |  | 0 |  |
| t30 | Hooks layer - validate-amount.py + validate-ownership.py, agent-hooks README, backend-imported hook test suite |  | 0 |  |
| t31 | MCP server core - transport-agnostic stdio JSON-RPC loop, config, JWT auth, copy-only manifest, structural gate |  | 0 |  |
| t32 | MCP tools and tests - four tool modules, hook wiring, package wiring, README, hermetic in-process test suite |  | 0 |  |
| t33 | Subagents - custom-agent/finance-analyst.md + qa-reviewer.md with frontmatter, .agents/agents symlinks |  | 0 |  |
| t34 | Extension-pack documentation - docs/agent-extension-pack.md overview + docs/permissions.md matrix |  | 0 |  |
| t35 | Agent-pack verification - criteria 12/7/9/10-12 + rows 31/32, REQ-PLAN-061 register, discovery re-proof, full composite |  | 0 |  |
| t36 | Scan pipeline - real make security targets (gitleaks/semgrep/trivy/pip-audit/npm-audit), pinned tool bootstrap, entry-#6 amend script authored |  | 0 |  |
| t37 | Dependency and secret scan reports - gitleaks/pip-audit/npm-audit committed artifacts as real measured runs |  | 0 |  |
| t42 |  |  | 0 |  |
| t39 | Ops runbook core - ops/runbook.md + health-check.md + logging.md | 2026-10-12 | 0 | e62b919 |
| t38 | Code and container scan reports - semgrep + trivy artifacts | 2026-10-12 | 0 | 2c9081f |
| t44 | Makefile security-semgrep --metrics off repair | 2026-10-12 | 0 | a64a3a2 |
| t43 | psycopg driver + connect-probe (E2E unblocker) | 2026-10-12 | 0 | de1c0e4 |
| t40 | Security documents - pr-audit, agent-security-notes (accepted-findings register), AI tool data policy | 2026-10-13 | 0 | 3c4036d |
| t46 | E2E uv-cache permission + CORS_ORIGINS JSON startup-config fix | 2026-10-13 | 0 | bb2eae1 |
| t41 | Security/ops verification generator + ops diagnosis & deployment-health records | 2026-10-13 | 0 | eba386e |
| t47 | Postgres migration portability - boolean defaults + portable year_month CHECK (E2E final blocker) | 2026-10-13 | 0 | fddadeb |
| t48 | Process/task-template/role/ownership docs (REQ-DOC-022/028/029/062/063) | 2026-10-13 | 0 | 28f60d6 |
| t49 | Root reviewer docs: CLAUDE.md, product-spec, openapi export, README criteria map + checklist + 5-min paths, runbook typo, render deviation | 2026-10-13 | 0 | 5e04b61 |
| t54 | E2E Playwright browser-version mismatch fix - e2e.yml installs browsers from the e2e workspace so the browser build matches pinned @playwright/test 1.58.0 (first-ever E2E green path, #45) | 2026-10-13 | 0 | 97153c0 |
| t50 | docs/ai-workflow.md - real session records, correction log, pack/review/data-policy, REQ-SEC-072 scan-timing section (closes SCAN_TIMING_DOC) | 2026-10-13 | 0 | 7264868 |
| t51 | Technical docs set - architecture/api/design-system/testing-guidelines against merged code (README pin-1 carried) | 2026-10-14 | 0 | 03010f7 |
| t55 | E2E first-ever-green fix - vite /api proxy + Start-the-frontend-dev-server step in e2e.yml (#45/#58/#59) | 2026-10-14 | 0 | bec01ab |
| t52 | REQ-DOC-040 screenshots - four PNGs + README pin-2 FINAL a64efaa2 (308L) | 2026-10-14 | 0 | 91936cb |
