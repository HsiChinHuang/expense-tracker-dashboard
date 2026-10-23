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
| t59 | Phase 9 exit composite - six generators + matrix 41d84eca 0-GAP, deferral re-attestation, floors 288/187/91/005, byte-pins, stored gates 226/17-pins, delta purity, all 7 fences verbatim with negative controls firing (phase_9 EXIT) | 2026-10-16 | 0 | 39d22fe |
| t60 | Navigation restructure: nest /expenses /budgets /categories under AppShell + 4th Expenses NavLink + "*" NotFound route (one-way-trap fix, REQ-FE-010/011, W5 re-mark, W9 guard-wrap) | #66 |
| t62 | npm-script dev workflow: root package.json check/setup:local/dev/stop + scripts/dev 5 node-builtin helpers, win32-native, Docker untouched (Q1/Q2/Q6, delta-purity fence form) | #68 |
| t63 | README Quick Start npm-first rewrite (check/setup:local/dev/stop primary, Stopping section, troubleshooting table, make demoted to Alternative, all-English; pin-2 retired, pin-3 f0fd9eda/367L) | #69 |
| t61 | Logout control into AppShell header (data-testid=logout-button, guard-wrapped); in-page dashboard logout removed (Q3a) | #67 |
| t65 | Demo-seed capability: backend/app/scripts/seed_demo.py (fixed demo@example.com/demo-password-123, 10 system categories, 90-day offset-pure dataset, per-month budgets, idempotent wipe+rebuild, non-demo byte-identical) + root npm seed:demo pinned line (no README touch, operator-directive anchor) | #71 |
| t66 | Reviewer-section relocation out of README: docs/verification.md + docs/development.md + docs/screenshots.md absorb detail, README 367->335 with Documentation map (exactly 3 one-line links) and full tests[128]/[201] compatibility surface kept; pin-3 untouched, tests[231] sanctioned RED leg; operator-approved README diff (phase_11 first README card) | #72 |
| t67 | README v2 sections 1-2: cold-reviewer pitch (one H1, 7-line first screen, zero internal vocabulary, phase-1 boilerplate replaced), Features + one-line screenshots link + full REQ-id citation preservation (60->60), honest Online demo (npm run seed:demo, demo@example.com/demo-password-123, live URL placeholder, zero fabricated URLs); 15/15 carried gates incl t66 family; pin-3 untouched, tests[231] sanctioned RED leg; orchestrator-signed Gate 3 under operator waiver 2026-10-15 | #73 |
| t68 | README v2 section 3: Prerequisites stated plainly - whole three-tool host list (Node.js 20+ with npm, uv, Git), no Python/Docker/make/bash knowledge needed, npm is the only daily command surface, section-isolated rewrite (everything outside byte-identical to base), no pins |
| t69 | README v2 sections 4-6: run-locally flow as EXACTLY EIGHT numbered steps (check, .env file, setup:local, dev, open localhost:5173, first-run register, seed:demo demo data, stop), seed:demo truth paragraph (demo-account-scoped wipe, deterministic), claims corroborated against dev.ts/seed_demo.py, no pins |
| t70 | README v2 sections 7-9: troubleshooting table re-voiced (4 carried row classes), ### API overview (docs/api.md + openapi.yaml, six paths + bearer), Render deployment as HONEST PLACEHOLDER (pending, #61 cited, no fabricated URL, tests[135] token set verbatim), procedure claims repo-backed |
| t71 | README v2 sections 10-12 + THE SINGLE PIN-4 SWITCHOVER: criteria mapping exactly 15 rows (tests[201]), Repository layout placeholder claim removed (e2e/ops/security exist), MIT + AI-workflow pointers, trailing CRLF; pin-4 LIVE by cross-consistency (README 58894964.../391 == docs_verification.py constants == regenerated report, differs from pin-2/pin-3/base); tests[227]+tests[231] retired-pin settlement by orchestrator ruling (Q1a), index never edited; 25/25 carried gates; Gate 3 under operator waiver with rigorous re-check |

| t64 | ? | 2026-10-14 | 0 | f538b198 |
| t90 | Gate amendment record for tests[133] (single-secret assertion -> closed two-secret allowlist, RE-PREMISE not relax) and committing the operator's deploy.yml RENDER_APP_URL edit | 2026-10-19 | 0 | 6fd2a0c |
| t91 | render.yaml CORS_ORIGINS moves to the live -1qtu Render domain as a quoted JSON array; APP_VERSION stays the quoted string "1.0.0"; tests[134] re-runs GREEN unchanged | 2026-10-18 | 0 | f181d65 |
| t92 | the phase_14 closeout evidence record - deploy run 39197889153 on merged bytes 0c3dd6d, its banked job log line, the live health corroboration, and the disclosed Render-log gap | 2026-10-19 | 0 | 8956d32d3a5ac0f31ad6df910745b420a0caab95 |
| t93 | "security_ops live-state move - RENDER_HEALTH_PATH to the -1qtu host, LIVE_DEPLOYMENT_STATE DEFERRED to VERIFIED, register 5 DEFERRED to 4 DEFERRED, criteria report regenerated, ops prose live, tests[187] RE-PREMISED" | 2026-10-19 | 0 | 24a0f4cd63517a994a03082ac201cf15ac9eee01 |
| t98 | "docs and infra live-state move - docs_verification register drops LIVE_DEPLOYMENT_STATE (4 to 3 DEFERRED, derived count), :422 and infra_verification :602 URLs to -1qtu, both reports regenerated, req matrix re-tallies 116/622/10, tests[218]/[219]/[221]/[223]/[224]/[226] RE-PREMISED" | 2026-10-19 | 0 | 5ba977579b001774513de37d9f6892a587a9618b |
| t94 | README live-URL backfill - Online demo and Deployment on Render state the -1qtu address honestly with no hosted demo account claimed, and the README triple pin moves in the same card | 2026-10-20 | 0 | 1f6fb4eb454377f7e780cecaa5a90045753120a6 |
| t95 | Close platform issue 61 with the bundled A3 plus B1a plus B1b plus B2 evidence - the deploy-hook secret residual is discharged, recorded once and traceably | 2026-10-20 | 0 | d794d2815a8d0d9ab11e5bf36e8db4377396ec21 |
| t96 | Remove the misleading Quick Start env-copy step from README and re-premise its coordinated gate set 232 250 251 plus the digest and line-count re-pin; the README 340 copy line stays | 2026-10-20 | 0 | 7e39de74aa866c5bea4ed8e9d5f2eddc1c249e43 |
| t97 | "Health version single source - backend/app/main.py line 81 builds FastAPI with version=get_settings().APP_VERSION so the health payload reports the configured 1.0.0 instead of the hardcoded 0.1.0" | 2026-10-18 | 0 | 9ffdbb0 |
| t109 | Hosted SPA asset resolution - register_spa_static mounts static_dir/SPA_ASSET_SUBDIR (assets) at the frozen /assets mount point so index-named bundle URLs resolve; test fixture re-shaped to the real Vite layout; strict, no flat fallback; openapi frozen, ZERO index bytes | 2026-10-22 | 0 | 009db2a |
| t110 | Root path serves the built SPA - GET / returns the built index.html via FileResponse when present while the route-free committed tree keeps the status-ok JSON; README names /api/v1/health as the operational probe inside the re-measured 396/f7c85e88 triple pin; re-premises the docs_verification CARRIED_DIGESTS drift; ZERO index bytes | 2026-10-22 | 0 | 0509310 |
| t112 | Scoring-map verification record - PROCESS cluster (Problem Description 2/2, Product Specification 2/2, Agent Team Specification 2/2, Context Management 2/2): docs/criteria/scoring_map/process.md with 30-second entry points, every number re-measured on base 6e36d4f, zero README/index/product bytes | 2026-10-23 | 0 | d961491 |
| t113 | Scoring-map verification record - APP cluster (Application 2/2, Testing 2/2 floor-41, Containerization 2/2 DB-OK postgres:16-alpine): docs/criteria/scoring_map/app.md, entry points exist on base, zero README/index/product bytes | 2026-10-23 | 0 | 8373176 |
| t114 | Scoring-map verification record - DELIVERY cluster (Deployment 2/2 live-probed twice, CI/CD 2/3 with priced gap + promote.yml prose-only honesty pair): docs/criteria/scoring_map/delivery.md, zero README/index/product bytes | 2026-10-23 | 0 | db2c2b8 |
| t115 | Scoring-map verification record - TELEMETRY cluster with deployed-vs-config-only classification (Observability 1/2 trace-ID capped, Alerting 1/1, On-Call 1/2 read-only capped; hosted /metrics = SPA html, Prometheus/Grafana/collector staged-config-only): docs/criteria/scoring_map/telemetry.md, zero README/index/product bytes | 2026-10-23 | 0 | aab1ce0 |
| t119 | Human-gated production promote pipeline: .github/workflows/promote.yml (workflow_dispatch + GitHub Environment 'production' required-reviewer gate + RENDER_DEPLOY_HOOK POST + deploy.yml-isomorphic 30x10s health retry + contents:read) + WAL-1268 R1/R2 carrier-set amendment in BOTH generators + both carried reports regenerated + R2 index amendments applied orchestrator-side same window | 2026-10-23 | 0 | cb3a038 |
