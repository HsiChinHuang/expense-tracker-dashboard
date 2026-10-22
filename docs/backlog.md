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
| t71 | README v2 sections 10-12 + SINGLE pin-4 switchover: criteria mapping (exactly-15 rows), project structure, license/AI-workflow pointers + README re-pin + tests[227] Q1a settlement + docs_verification.py pin repair + report regeneration | [t70] | #77 | closed |
| t72 | README offline-verification hotfix: explicit npm install step, honest optional .env step naming backend/.env, tsx troubleshooting row, seed:demo second-terminal truth + SINGLE pin-5 switchover by cross-consistency | [] | #78 | defined |
| t73 | Expense form category dropdown: replace the bare Category-id UUID input with a select fed by use_categories (frontend only; e2e + form pins dispositioned) | [] | #79 | defined |
| t74 | Category form colour/icon UX: native colour picker + #RRGGBB text field with example, live swatch, #6B7280 default, client-side validation quoted from backend/app/schemas/category.py (frontend only) | [] | #80 | closed |
| t75 | Observability skeleton - observability/README.md plus observability/compose.yaml with Prometheus, Alertmanager and Grafana enabled and the OTel collector / Loki / Tempo block commented optional, on a port band colliding with neither 8001 nor 8137 | [] | #81 | closed |
| t76 | Prometheus scrape config and the alerts authority - observability/prometheus.yml plus observability/alerts.yaml, the single source of truth for every alert name and metric name used by any other card in this milestone | [t75] | #82 | closed |
| t77 | Grafana dashboard and the optional collector config - observability/dashboard.json with panels for expense creation rate, creation failure rate and fallback state, plus observability/collector.yaml as the documented optional OTel collector | [t76] | #83 | closed |
| t78 | OTel metrics substrate - backend/app/telemetry.py plus the dependency, app-factory wiring and test, exposing a local-only /metrics endpoint with service.name, deployment.environment and service.version resource attributes | [] | #84 | closed |
| t79 | Business counters on the merged create paths - expense_created_total, expense_create_failures_total and category_created_total, with metric names matching observability/alerts.yaml verbatim | [t78, t76] | #85 | closed |
| t80 | Incident-response evidence collector - incident-response/collect-evidence.sh plus README.md, gathering health, /metrics, a log tail and the version into the incident evidence directory, with a --simulate-fallback mode producing real degraded evidence | [] | #86 | closed |
| t81 | Responder prompt and response schema - incident-response/responder-task.md plus incident-response/response.schema.json and a pinned validator, so an AI on-call pass over an evidence bundle produces a machine-checkable answer | [t80] | #87 | closed |
| t82 | Autonomy policy and runbooks - incident-response/autonomy-policy.yaml denying restart, DB mutation and merge, allowing read-only reads and report writing, plus rollback.sh and verify-recovery.sh asserting status ok with fallback_active false | [t80] | #88 | closed |
| t83 | Incidents scaffold and the incident-ID authority - incident-response/incidents/README.md plus the 2026-10-17-db-fallback-01 directory whose alert.json is a verbatim copy of the DBFallbackActive entry from observability/alerts.yaml | [t76, t80] | #89 | closed |
| t84 | Measured drill and incident record - run the t80 harness for real degraded evidence in 2026-10-17-db-fallback-01, land a schema-valid response.json from an AI on-call pass, and a resolution.md with the recovery-verification output and a timeline | [t80, t81, t82, t83, t78, t79] | #90 | closed |
| t85 | Diagnosis rewrite to alert-driven - ops/diagnosis.md and ops/runbook.md re-voiced around the firing alert (name verbatim from observability/alerts.yaml) and the measured evidence, ADD-only so t41 gate strings survive byte-identical | [t84, t76] | #91 | defined |
| t86 | Scan refresh - re-run all five committed security reports against the final merged tree so their timestamps and tree hash describe the code a reviewer will actually audit | [t84] | #92 | defined |
| t87 | Accepted-findings refresh - bind every finding the refreshed scans surfaced to a disposition in security/agent-security-notes.md and record the traces gap as a documented limitation in security/ai-tool-data-policy.md | [t86] | #93 | defined |
| t88 | Reviewer report - docs/operations-and-security-report.md carrying the PR audit, scan summary, agent and extension security, operational diagnosis, AI tool policy, incident reconstruction chain, limitations and improvements | [t85, t87] | #94 | defined |
| t89 | Evidence map and criteria closeout - the README criterion-13 row gains the new artifacts within a hard 3-line budget with a pinned wc -l check, and docs/criteria/security_ops_verification.md records the phase_13 evidence rows | [t88] | #95 | defined |
| t90 | Gate amendment record for tests[133] (single-secret assertion -> closed two-secret allowlist, RE-PREMISE not relax) and committing the operator's deploy.yml RENDER_APP_URL edit | [] | #96 | closed |
| t91 | render.yaml CORS_ORIGINS moves to the live -1qtu Render domain as a quoted JSON array; APP_VERSION stays the quoted string "1.0.0"; tests[134] re-runs GREEN unchanged | [] | #97 | closed |
| t92 | Real workflow_run green evidence for the two-secret deploy job - the run id, the deploy verified: health endpoint is ok log line and the Render build/migration logs, closing the REQ-CICD-034 final-step gap | [t90, t91] | #98 | closed |
| t93 | security_ops live-state move - RENDER_HEALTH_PATH to the -1qtu host, LIVE_DEPLOYMENT_STATE DEFERRED to verified, register 5 to 4 DEFERRED, criteria report regenerated, ops prose live, tests[187] re-premised | [t92] | #99 | closed |
| t98 | docs and infra live-state move - docs_verification register drops LIVE_DEPLOYMENT_STATE (4 to 3 DEFERRED, derived count), :422 and infra_verification :602 URLs to -1qtu, both reports regenerated, tests[219]/[223]/[226] re-premised | [t92, t93] | #100 | closed |
| t94 | README live-URL backfill - Online demo and Deployment on Render state the -1qtu address honestly with no hosted demo account claimed, and the README triple pin moves in the same card | [t98] | #101 | closed |
| t95 | Close platform issue 61 with the bundled A3 plus B1a plus B1b plus B2 evidence - the deploy-hook secret residual is discharged, recorded once and traceably | [t92, t93, t98, t94] | #102 | closed |
| t96 | Remove the misleading Quick Start env-copy step from README and re-premise its coordinated gate set 232 250 251 plus the digest and line-count re-pin; the README 340 copy line stays | [] | #103 | closed |
| t97 | Health version single source - backend/app/main.py builds FastAPI with version=settings.APP_VERSION so the live health payload reports 1.0.0 instead of the hardcoded 0.1.0 | [] | #104 | closed |
| t99 | Coordinated index-anchor amendment record for tests[190] and tests[191] - the two stored byte-pins of tests[133] drop the pre-t90 digest 6e9723e8 for the as-shipped 09cb7d9a, re-premise not relax, delivered as a record the orchestrator applies in the merge window | [] | #105 | closed |
| t100 | Generator-side anchor re-premise - docs_verification.py INDEX_ANCHORS[133] to 09cb7d9a and regenerate the committed verification report; the only predicted baseline change 33 to 32 with leg 258 recovering and leg 259 named retired | [t99] | #106 | closed |
| t101 | Premise-correction record for the t95 option-A defects - leg 214 is GREEN on a clean checkout so the gate matrix must not premise build-dir pollution, and leg 255's authoritative pin is the post-t94 f5aafe07 not the pre-t94 9aac9f0c | [] | #107 | closed |
| t102 | Pollution-boundary hardening - SKIP_DIRS excludes build and scratch so copy-junction dirt cannot reach the verification walk, plus the recorded four-class pollution policy naming the sweep-runner allowlist obligation | [t100] | #108 | closed |
| t103 | Criteria-docs staleness refresh - regenerate docs/criteria/agent_pack_verification.md and docs/criteria/req_coverage_verification.md from their own generators so the committed evidence matches current-tree truth, with the stored-leg hazard derived and replayed rather than quoted | [] | #109 | defined |
| t104 | Repo-hygiene batch - gitignore scratch/ per the operator decision, codify the cmd.exe-vs-WSL environment rules in docs/commands.md, and ship the all-leg literal docs/issues/tXX.md path-pin audit as a checker plus findings with the t78 exemption documented and the index never patched | [] | #110 | defined |
| t105 | Index re-premise for the 11 base64-hidden card-path pins - tests[282] t76-ac4 and tests[306..309] t86-ac1..4 and tests[310..312] t87-ac1..3 and tests[315..317] t88-ac1..3 (0-based array indices): edit ONLY those 11 legs' base64 payloads so their probes reference docs/issues/closed/, with blob-level proof the other 307 legs are byte-identical; THIS card amends index ownership IN WRITING (operator authorization WAL 1241, THIS card only) | [] | #111 | defined |
| t106 | Checker b64 upgrade - docs/tools/leg_path_pin_audit.py gains a decoded-base64 view so the WAL 1236 hidden-pin class is visible, while plaintext detection stays byte-stable (legs 230/279 findings print identically to the t104 record); ship the superset findings record; ZERO index bytes on this card (index ownership is t105's amendment alone) | [] | #112 | defined |
| t107 | Findings-record index stamping - docs/tools/leg_path_pin_audit.py gains --against-record (UNSTAMPED note exit 0 / same-blob EXPECTED exit 0 / same-blob DRIFT exit 1 with the gate line / cross-blob EXPECTED exit 0) and a NEW stamped companion record docs/state/outputs/t107_record_stamp_findings.json ships, generated by running the tool on the merged index; the t104/t106 records stay byte-frozen and gain no index_stamp key, regeneration (option a) is REJECTED, and this card carries ZERO index bytes so the WAL 1248 W2 eight-property amendment policy is NOT invoked | [] | #113 | defined |
| t108 | plan.md phase_17 vocabulary cleanup - the disposition line states the shipped pair (read_closed for the 3 live readers 282/308/309 vs guard_correct_semantics for the 8 dead-constant legs 306/307/310/311/312/315/316/317, 0-based array indices) instead of the hygiene-move drift word, and the rejected skipped-probe mechanism prose at lines 2488-2489 goes while the MEASURED-liveness sentence stays; docs-only, plan.md ONLY (the phase_17 handoffs are historical records and are NOT rewritten), zero product bytes | [] | #114 | defined |
| t109 | Hosted SPA asset resolution - backend/app/main.py register_spa_static mounts static_dir / SPA_ASSET_SUBDIR (new module constant, "assets") at the UNCHANGED frozen SPA_MOUNT_PATH /assets instead of the copied dist root, so the URLs index.html names resolve; backend/tests/unit/test_static_serving.py _build_static is RE-SHAPED to the real Vite layout (index.html at the static root, the hashed bundle below assets/) so the three frozen pytest node IDs of tests[130] t24 can never again pass on a false premise; STRICT with no flat-repo fallback; openapi.yaml byte-frozen, ZERO index bytes, the GET / handler region byte-identical for the sibling | [] | #115 | defined |
| t110 | Root path serves the built SPA - GET / returns the built index.html as text/html when a frontend is present while the route-free committed tree keeps {"status":"ok"} (the recorded ruling, which is what lets tests[130]'s frozen paths.count("/")==1 and unknown-path-404 assertions survive with NO written amendment); shipped as one FileResponse plus one sanctioned type: ignore so openapi.yaml does not move; the README live-URL guidance names /api/v1/health as the operational probe (line-neutral inside the 396-line/17-heading/13-hex triple pin, digest and report re-measured per t96/t100); re-premises the one pre-existing docs_verification CARRIED_DIGESTS drift that blocks tests[258] | [t109] | #116 | defined |

## HELD - recorded, NOT dispatched (phase_19 survey, 2026-10-22)

Two items were evaluated at survey and deliberately NOT turned into cards. They are
recorded here so the next survey inherits the reasoning rather than the oversight.

- **A hosted leg that fetches a real frontend asset (closing the phase_19 blind spot
  (c)).** The six hosted legs in the merge index (t26, t41, t57, t58, t59, t70) probe
  `/api/v1/health` and README text and NONE fetches a frontend asset, which is why the
  blank-page defect (t109) could ship behind a green sweep. RULING at phase_19 survey:
  NOT now, on both cards. Adding a leg is an INDEX AMENDMENT and would invoke the full
  WAL 1248 W2 eight-property policy, and the leg would be RED-BY-CONSTRUCTION at the
  merge moment (the deployed bytes are still the broken ones until t109 ships), which
  teaches the sweep to ignore a permanently-red leg - the blind spot in a new costume.
  The defect CLASS is closed without the index: t109's re-shaped fixture runs under the
  already-frozen tests[130] (t24) in every merge sweep. CONSTRAINT ON WHOEVER BUILDS
  THIS LATER: the leg MUST parse the deployed index.html at run time and fetch what THAT
  document references, and MUST NEVER pin a hashed filename - hashed names change on
  every frontend rebuild, so a pinned name rots and re-creates the same blind spot.
- **tests[227] (t59 ac4) carries a stale README premise.** It pins `README.md` at 308
  lines and cr-stripped digest `a64efaa2...` while the shipped README is 396 lines /
  `15b24413...` (measured at groom on main tip). The premise was left stale by the
  post-t94 README growth (t94/t96 moved the README; leg 227's pin was not carried with
  it), so the leg is RED AT BASE and stays RED - t109/t110 do not cause it and do not
  claim to fix it. Repairing the pin is an INDEX WRITE, i.e. an amendment this phase
  explicitly declines to make (zero index bytes on both cards). The same leg's
  `openapi.yaml` half IS green (pinned `6f2a0a3d...` matches) and both cards keep it
  green. A future card should re-premise leg 227's README half to the then-shipped bytes
  under the eight-property policy, not relax it.
