# Backlog

| ID | Title | Depends | Platform | Status |
|---|---|---|---|---|
| t0 | Repository skeleton per Chapter 16 structure | [] | #3 | closed |
| t1 | Backend skeleton (FastAPI + uv + pytest + ruff/mypy) | [t0] | #4 | closed |
| t2 | Frontend skeleton (Vite + React + TS + Tailwind + Vitest) | [t0] | #5 | closed |
| t3 | Health check endpoint GET /api/v1/health | [t1] | #6 | closed |
| t4 | Root configuration files (.env.example, Makefile, LICENSE, README) | [t1, t2] | #7 | closed |
| t5 | Database foundation - Settings, SQLAlchemy engine/session, Alembic wiring | [t1, t4] | #8 | closed |
| t6 | User model and users-table Alembic migration | [t5] | #9 | closed |
| t7 | Auth primitives - bcrypt password hashing and HS256 JWT module | [t5, t6] | #10 | closed |
| t8 | Register / login / me endpoints with auth service and get_current_user | [t7] | #11 | closed |
| t9 | Frontend auth - axios client, AuthContext, route guards, login/register pages | [t2, t8] | #12 | closed |
| t10 | Category model, Alembic revision 002, idempotent system-category seed | [t5, t6] | #13 | closed |
| t11 | Categories API - list/create/delete with system protection and access validator | [t8, t10] | #14 | closed |
| t12 | Audit foundation - audit_logs model, Alembic 003, same-transaction logger, get_client_ip | [t6, t10] | #15 | closed |
| t13 | Expenses vertical - model + Alembic 004, service, five endpoints, audit integration | [t11, t12] | #16 | closed |
| t14 | Budgets vertical - model + Alembic 005, upsert/get/delete endpoints, audit integration | [t12, t13] | #17 | closed |
| t15 | Cross-resource user-isolation and money-precision test suite | [t13, t14] | #18 | closed |
| t16 | Frontend data layer - typed api modules, queryKeys, CRUD hooks, MSW handlers | [t9, t13, t14] | #19 | closed |
| t17 | ExpensesPage + ExpenseForm modal + ToastProvider (network-error presentation) | [t16] | #20 | closed |
| t18 | BudgetPage + CategoriesPage | [t16] | #21 | closed |
| t19 | Dashboard backend - dashboard_service helpers and six GET endpoints | [t14] | #22 | closed |
| t20 | Frontend dashboard data layer - MonthContext, dashboard api/hooks, EmptyState/ErrorState | [t17, t19] | #23 | closed |
| t21 | Recharts admission and four chart components (pie, trend, cumulative, heatmap) | [t20] | #24 | closed |
| t22 | DashboardPage - MonthPicker, KPI cards, BudgetProgress, recent list, chart wiring, edge cases | [t20, t21] | #25 | closed |
| t23 | Dashboard verification - REQ-PLAN-041 cross-checks, criteria rows, performance measurement | [t19, t22] | #26 | closed |
| t24 | Containerization - multi-stage Dockerfile, docker-compose db+app, .dockerignore, README local modes | [t23] | #27 | closed |
| t25 | SQLite fallback - create_db_engine PostgreSQL timeout chain, fallback create_all + seed, live health reporting | [t23] | #28 | closed |
| t26 | CI/CD and Render - ci.yml e2e.yml deploy.yml workflows, render.yaml, Makefile test targets, README deploy notice | [t24, t25] | #29 | closed |
| t27 | Playwright E2E harness - e2e workspace, config, fixtures, three specs, Makefile e2e target | [t26] | #30 | closed |
| t28 | Infra verification - criteria 8/10/11 + rows 29/30, fallback timing evidence, deferral register, full-suite composite | [t26, t27] | #31 | closed |
| t29 | Skills layer - three SKILL.md documents, .agents/skills symlinks, canonical discovery gate | [t28] | #32 | closed |
| t30 | Hooks layer - validate-amount.py + validate-ownership.py, agent-hooks README, backend-imported hook test suite | [t28] | #33 | closed |
| t31 | MCP server core - transport-agnostic stdio JSON-RPC loop, config, JWT auth, copy-only manifest, structural gate | [t29] | #34 | closed |
| t32 | MCP tools and tests - four tool modules, hook wiring, package wiring, README, hermetic in-process test suite | [t30, t31] | #35 | closed |
| t33 | Subagents - custom-agent/finance-analyst.md + qa-reviewer.md with frontmatter, .agents/agents symlinks | [t29] | #36 | closed |
| t34 | Extension-pack documentation - docs/agent-extension-pack.md overview + docs/permissions.md matrix | [t29, t30, t32, t33] | #37 | closed |
| t35 | Agent-pack verification - criteria 12/7/9/10-12 + rows 31/32, REQ-PLAN-061 register, discovery re-proof, full composite | [t29, t30, t32, t33, t34] | #38 | closed |
| t36 | Scan pipeline - real make security targets (gitleaks/semgrep/trivy/pip-audit/npm-audit), pinned tool bootstrap, entry-#6 amend script authored | [t35] | #39 | closed |
| t37 | Dependency and secret scan reports - gitleaks/pip-audit/npm-audit committed artifacts as real measured runs | [t36] | #40 | closed |
| t38 | Code and container scan reports - semgrep and trivy committed artifacts completing the five-report set | [t36, t37] | #41 | closed |
| t39 | Ops runbook core - ops/runbook.md seven symptom sections + escalation, ops/health-check.md, ops/logging.md seventeen-event table | [t36] | #42 | closed |
| t40 | Security documents - pr-audit record, agent-security-notes with accepted-findings register, ai-tool-data-policy | [t37, t38, t39] | #43 | closed |
| t41 | Security and ops verification - criteria 13 evidence generator, ops diagnosis + deployment-health, deferral register, milestone-exit composite | [t36, t37, t38, t39, t40] | #44 | closed |
| t42 | CI/E2E runner repair - setup-uv pin, coverage-v8 devDep, actions/cache v5, E2E wait diagnostics | [t35] | #45 | closed |
| t43 | psycopg driver repair - psycopg[binary] + connect-probe inside sqlite-fallback try (E2E unblocker) | [t42] | #46 | closed |
| t45 | E2E app container startup diagnosis - surface container logs on health-wait failure | [t42] | #48 | closed |
| t46 | E2E uv-cache permission fix - runtime user app cannot init root-owned /tmp/uv-cache (measured: Permission denied; container dies 0.1s) | [t42] | #49 | closed |
| t47 | Postgres migration portability - boolean defaults + portable year_month CHECK + DDL-pin tests (E2E final blocker) | [t46] | #50 | closed |
| t44 | Makefile security-semgrep recipe repair - remove --metrics off conflicting with --config auto in semgrep 1.180.0 | [t36] | #47 | closed |
| t48 | Process/task-template/role docs - docs/process.md, docs/task-template.md, docs/team/*, docs/ownership.md | [t41] | #51 | closed |
| t49 | Root reviewer docs (CLAUDE.md, product-spec, openapi export, README criteria map, runbook typo, render deviation) | [t48] | #52 | closed |
| t50 | docs/ai-workflow.md - real session records, correction log, pack/review/data-policy, REQ-SEC-072 scan-timing section (closes SCAN_TIMING_DOC) | [t48, t49] | #53 | closed |
| t51 | Technical docs set - docs/architecture.md, docs/api.md, docs/design-system.md, docs/testing-guidelines.md against merged code | [t49] | #54 | closed |
| t52 | Screenshots - dashboard/expense-form/budget-page/health-check PNGs from a measured run + README pointers (final README pin) | [t50, t51] | #55 | closed |
| t53 | Documentation verification - docs_verification generator, Chapter 24.3 rows 1-15, deferral re-test, project-wide exit composite | [t48, t49, t50, t51, t52] | #57 | closed |
| t54 | E2E Playwright browser-version mismatch fix - e2e.yml installs browsers from the e2e workspace so the browser build matches pinned @playwright/test 1.58.0 (first-ever E2E green path, #45) | [t47] | #58 | closed |
| t55 | E2E suite targets localhost:5173 but the CI stack serves the SPA on :8000 - no frontend server for the suite run (first-ever E2E green final blocker) | [t54] | #59 | closed |
| t56 | E2E registerUser helper strict-mode violation - getByLabel Password matches two inputs (first-ever fully-green E2E blocker) | [t55] | #60 | closed |
| t57 | Per-REQ-ID coverage matrix generator - req_coverage_verification.py + docs/criteria/req_coverage_verification.md (749 ids, closed vocabulary, evidence pointers, fail-closed fence) | [t53] | #62 | closed |
| t58 | Per-REQ-ID gap remediation - author missing evidence artifacts (predicted: PLAN risk/workflow records, STRUCT file-count + naming, DB-120/ARCH-081 assumptions, TEST-070 list, PROD success rows) until the t57 fence reaches 0 GAP | [t57] | #63 | closed |
| t59 | Requirement-coverage verification composite - six generators green, 749-row matrix closed at 0 GAP, floors + byte-pins + deferral re-attestation (phase_9 exit card) | [t57, t58] | #64 | closed |
| t60 | Navigation restructure: nest /expenses /budgets /categories under AppShell + '*' NotFound route + Expenses nav link (one-way-trap fix, REQ-FE-010/011) | [] | #66 | closed |
| t61 | Logout control into AppShell header (data-testid logout-button, Q3a); remove dashboard in-page logout; AuthContext.logout untouched | [t60] | #67 | closed |
| t62 | npm-script dev workflow in ROOT package.json: check (Q6 auto-fix) / setup:local / dev / stop (Windows-11-first, node builtins only, zero new deps, Docker banned) | [] | #68 | closed |
| t63 | README Quick Start rewrite (ALL ENGLISH): npm-script path first, Stopping the app, troubleshooting table, make demoted to Alternative; pin-2 retired -> pin-3 appended per Q1a | [t60, t62] | #69 | closed |
| t64 | phase_10 exit composite: full index replay minus retired tests[227] + pin-3 green + floors + byte-pins + matrix rows re-marked + dev-workflow probes (milestone exit) | [t60, t61, t62, t63] | #70 | closed |
| t65 | Demo-seed product capability: backend/app/scripts/seed_demo.py + root npm script seed:demo (demo@example.com fixed, idempotent wipe+rebuild, non-demo users untouched, no README touch) | [] | #71 | closed |
| t66 | Move internal reviewer sections out of README.md into docs/verification.md, docs/development.md, docs/screenshots.md with one-line README links (no pins; tests[128] token set preserved) | [t65] | #72 | closed |
| t67 | README v2 sections 1-2: pitch, features, screenshots link, online-demo placeholder with the fixed demo account (no pins) | [t66] | #73 | closed |
| t68 | README v2 section 3: Prerequisites stated plainly - no Python/Docker/make knowledge needed, npm only (no pins) | [t67] | #74 | closed |
| t69 | README v2 sections 4-6: run-locally flow npm run check / cp .env.example .env / setup:local / dev / open http://localhost:5173, first-run register, seed:demo demo data, npm run stop (no pins) | [t68] | #75 | closed |
| t70 | README v2 sections 7-9: troubleshooting, API overview, Render deployment PLACEHOLDER only - carried tests[135] heading/token set preserved, residual #61 cited (no pins) | [t69] | #76 | closed |
| t71 | README v2 sections 10-12 + SINGLE pin-4 switchover: criteria mapping (exactly-15 rows), project structure, license/AI-workflow pointers + README re-pin + tests[227] Q1a settlement + docs_verification.py pin repair + report regeneration | [t70] | #77 | defined |
