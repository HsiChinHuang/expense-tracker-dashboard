# Closed issues
Runtime-maintained by Orchestrator.

| ID | Title | Closed At | Retries | Merge Commit |
|---|---|---|---|---|
| t0 | Repository skeleton per Chapter 16 structure | 2026-10-07 | 0 | 1753fd07205d61318253fa1e20877ae4e1d2535a |
| t1 | Backend skeleton (FastAPI + uv + pytest + ruff/mypy) | 2026-10-07 | 0 | 792f644451529af3d59bcff4de11b36f3cee1f74 |
| t2 | Frontend skeleton (Vite + React + TS + Tailwind + Vitest) | 2026-10-07 | 1 | 4f89797b4af95195132b7490965d93c65dd5bb73 |
| t3 | Health check endpoint GET /api/v1/health | 2026-10-07 | 0 | b3c5746861502cf3c777554e4310e86c931d4283 |
| t4 | Root configuration files (.env.example, Makefile, LICENSE, README) | 2026-10-07 | 0 | 410ac3e8df72ea5afd6e7bbb05004686051ded7f |
| t5 | Database foundation - Settings, SQLAlchemy engine/session, Alembic wiring | 2026-10-07 | 0 | 8e9fcb388 |
| t6 | User model and users-table Alembic migration | 2026-10-07 | 0 | 17064fcd6 |
| t7 | Auth primitives - bcrypt password hashing and HS256 JWT module | 2026-10-07 | 0 | d189d2d |
| t8 | Register / login / me endpoints with auth service and get_current_user | 2026-10-08 | 1 | 8298a0b |
| t9 | Frontend auth - axios client, AuthContext, route guards, login/register pages | 2026-10-08 | 0 | 1a89838 |
| t10 | Category model, Alembic revision 002, idempotent system-category seed | 2026-10-08 | 0 |  |
| t11 | Categories API - list/create/delete with system protection and access validator | 2026-10-08 | 0 |  |
| t12 | Audit foundation - audit_logs model, Alembic 003, same-transaction logger, get_client_ip | 2026-10-08 | 0 |  |
| t13 | Expenses vertical - model + Alembic 004, service, five endpoints, audit integration | 2026-10-08 | 0 |  |
| t14 | Budgets vertical - model + Alembic 005, upsert/get/delete endpoints, audit integration | 2026-10-08 | 0 | 740223c |
| t15 | Cross-resource user-isolation and money-precision test suite | 2026-10-08 | 0 | 32bc15c |
| t16 | Frontend data layer - typed api modules, queryKeys, CRUD hooks, MSW handlers | 2026-10-08 | 0 | 6dbf552 |
| t17 | ExpensesPage + ExpenseForm modal + ToastProvider (network-error presentation) | 2026-10-08 | 0 | 3333abc |
| t18 | BudgetPage + CategoriesPage | 2026-10-08 | 0 | cde20ee |
| t19 | Dashboard backend - dashboard_service helpers and six GET endpoints | 2026-10-09 | 0 | 5d0165d |
| t20 | Frontend dashboard data layer - MonthContext, dashboard api/hooks, EmptyState/ErrorState | 2026-10-09 | 0 | 7b48199 |
| t21 | Recharts admission and four chart components (pie, trend, cumulative, heatmap) | 2026-10-09 | 0 | 1eebbca |
| t22 | DashboardPage - MonthPicker, KPI cards, BudgetProgress, recent list, chart wiring, edge cases | 2026-10-09 | 0 | d589c4e |
| t23 | Dashboard verification - REQ-PLAN-041 cross-checks, criteria rows, performance measurement | 2026-10-09 | 0 | 5eb1368 |
| t24 | Containerization - multi-stage Dockerfile, docker-compose db+app, .dockerignore, README local modes | 2026-10-09 | 0 | e416bf1 |
| t25 | SQLite fallback - create_db_engine PostgreSQL timeout chain, fallback create_all + seed, live health reporting | 2026-10-09 | 0 | b6008f4 |
| t26 | CI/CD and Render - ci.yml e2e.yml deploy.yml workflows, render.yaml, Makefile test targets, README deploy notice | 2026-10-09 | 0 | d3e1845 |
| t27 | Playwright E2E harness - e2e workspace, config, fixtures, three specs, Makefile e2e target | 2026-10-10 | 0 | 3f097a7 |
| t28 | Infra verification - criteria 8/10/11 + rows 29/30, fallback timing evidence, deferral register, full-suite composite | 2026-10-10 | 0 | feb7352 |
| t29 | Skills layer - three SKILL.md documents, .agents/skills symlinks, canonical discovery gate | 2026-10-10 | 0 | 23019ff |
| t30 | Hooks layer - validate-amount.py + validate-ownership.py, agent-hooks README, backend-imported hook test suite | 2026-10-10 | 0 | c5e4fdb |
| t31 | MCP server core - transport-agnostic stdio JSON-RPC loop, config, JWT auth, copy-only manifest, structural gate | 2026-10-10 | 0 | b873053 |
| t32 | MCP tools and tests - four tool modules, hook wiring, package wiring, README, hermetic in-process test suite | 2026-10-10 | 0 | 127d7bd |
| t33 | Subagents - custom-agent/finance-analyst.md + qa-reviewer.md with frontmatter, .agents/agents symlinks | 2026-10-10 | 0 | ff76141 |
| t34 | Extension-pack documentation - docs/agent-extension-pack.md overview + docs/permissions.md matrix | 2026-10-11 | 0 | 6510b60 |
| t35 | Agent-pack verification - criteria 12/7/9/10-12 + rows 31/32, REQ-PLAN-061 register, discovery re-proof, full composite | 2026-10-11 | 0 | 955aec4 |
| t36 | Scan pipeline - real make security targets (gitleaks/semgrep/trivy/pip-audit/npm-audit), pinned tool bootstrap, entry-#6 amend script authored | 2026-10-12 | 0 | 7d5c328 |
| t37 | Dependency and secret scan reports - gitleaks/pip-audit/npm-audit committed artifacts as real measured runs | 2026-10-12 | 0 | 0aa86ff |
| t42 |  | 2026-10-12 | 0 | 0f37141 |
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
| t56 | E2E registerUser strict-mode repair - first-ever fully-green E2E candidate (#60) | 2026-10-14 | 0 | 2e5f3e1 |
| t53 | Documentation verification - docs_verification generator + generated doc, Chapter 24.3 rows 1-15, deferral re-test, project-wide exit composite (LAST CARD) | 2026-10-14 | 1 | 9557f46 |
| t57 | Per-REQ-ID coverage matrix generator - req_coverage_verification.py + docs/criteria/req_coverage_verification.md (749 ids, closed vocabulary, evidence pointers, fail-closed fence; 99 measured GAP rows handed to t58) | 2026-10-15 | 1 | 335f822 |
| t58 | Close all 99 GAP rows in the REQ coverage matrix - 97 evidence-closure citations across 10 docs + 2 ruling-mapped DEFERRED_RULLED (#65), generator 0-GAP exit, matrix digest 41d84eca | 2026-10-15 | 1 | d7b95cb |
